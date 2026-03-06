from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import jwt
import datetime
import random
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import uuid
import json

# Load environment variables
load_dotenv()

import gzip
import io
import base64
import subprocess
import tempfile

app = Flask(__name__)
# Enable CORS for all domains on all routes
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", compression=True) # Enable SocketIO compression

# Config
basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 100 * 1024 * 1024))
db = SQLAlchemy(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    nickname = db.Column(db.String(50))
    avatar = db.Column(db.String(200))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Canvas(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), default="未命名画布")
    content = db.Column(db.Text, default='{"nodes":[], "edges":[]}')
    is_public = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(255), nullable=True)
    allow_guest_edit = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def set_password(self, password):
        if password:
            self.password_hash = generate_password_hash(password)
        else:
            self.password_hash = None
            
    def check_password(self, password):
        if not self.password_hash:
            return True
        return check_password_hash(self.password_hash, password)

class SharedContent(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    canvas_id = db.Column(db.String(36), db.ForeignKey('canvas.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    node_ids = db.Column(db.Text, nullable=False) # JSON list of node IDs
    settings = db.Column(db.Text, default='{}') # JSON for password, permissions, etc.
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    canvas = db.relationship('Canvas', backref=db.backref('shares', lazy=True))
    owner = db.relationship('User', backref=db.backref('shares', lazy=True))

class CanvasHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(db.String(36), db.ForeignKey('canvas.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Who made the change
    content = db.Column(db.Text, nullable=False) # JSON string
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    canvas = db.relationship('Canvas', backref=db.backref('history', lazy=True, order_by="desc(CanvasHistory.created_at)"))
    user = db.relationship('User')

# In-memory store for verification codes (for demo purposes)
verification_codes = {}
# In-memory store for active users in rooms

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.datetime.utcnow().isoformat()}), 200

room_users = {}

# Helper to verify token
def token_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

# Optional token check for public access
def get_current_user_optional():
    token = None
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
    
    if token:
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            return User.query.get(data['user_id'])
        except:
            pass
    return None

# Routes
@app.route('/api/send-code', methods=['POST'])
def send_code():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'message': 'Email is required'}), 400
    
    code = str(random.randint(100000, 999999))
    verification_codes[email] = code
    
    # In a real app, send email here. For now, print to console.
    print(f"VERIFICATION CODE for {email}: {code}")
    
    return jsonify({'message': 'Verification code sent (check console)', 'code': code}) # Returning code for easier testing

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    code = data.get('code')
    
    if not email or not password or not code:
        return jsonify({'message': 'Missing fields'}), 400
        
    if verification_codes.get(email) != code:
        return jsonify({'message': 'Invalid verification code'}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 400
        
    new_user = User(email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    # Cleanup code
    del verification_codes[email]
    
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'message': '邮箱或密码错误'}), 401
        
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({
        'token': token, 
        'email': email,
        'nickname': user.nickname,
        'avatar': user.avatar
    })

@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    code = data.get('code')
    
    if not email or not password:
        return jsonify({'message': '请输入邮箱和密码'}), 400
        
    user = User.query.filter_by(email=email).first()
    
    if user:
        # Existing user: Login
        if not user.check_password(password):
            return jsonify({'message': '密码错误'}), 401
            
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'token': token, 
            'email': email, 
            'action': 'login',
            'nickname': user.nickname,
            'avatar': user.avatar
        })
    else:
        # New user: Register
        if not code:
            return jsonify({'message': '新用户请填写验证码以完成注册', 'require_code': True}), 400
            
        if verification_codes.get(email) != code:
            return jsonify({'message': '验证码错误'}), 400
            
        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        # Cleanup code
        if email in verification_codes:
            del verification_codes[email]
            
        token = jwt.encode({
            'user_id': new_user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'token': token, 
            'email': email, 
            'action': 'register',
            'nickname': new_user.nickname,
            'avatar': new_user.avatar
        })

@app.route('/api/user/profile', methods=['GET', 'PUT'])
@token_required
def update_profile(current_user):
    if request.method == 'GET':
        return jsonify({
            'nickname': current_user.nickname,
            'avatar': current_user.avatar,
            'email': current_user.email
        })

    data = request.get_json()
    nickname = data.get('nickname')
    
    if nickname is not None:
        current_user.nickname = nickname
        db.session.commit()
        
    return jsonify({
        'message': '个人信息已更新',
        'nickname': current_user.nickname,
        'avatar': current_user.avatar
    })

@app.route('/api/user/avatar', methods=['POST'])
@token_required
def upload_avatar(current_user):
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
        
    if file:
        filename = secure_filename(f"avatar_{current_user.id}_{int(datetime.datetime.now().timestamp())}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Generate URL
        avatar_url = f"/api/uploads/{filename}"
        current_user.avatar = avatar_url
        db.session.commit()
        
        return jsonify({
            'message': '头像已上传',
            'avatar': avatar_url
        })

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
        
    return jsonify({
        'id': user.id,
        'email': user.email, # Maybe hide email for privacy? Keeping it for now as per context
        'nickname': user.nickname,
        'avatar': user.avatar
    })

@app.route('/api/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'message': '请输入原密码和新密码'}), 400
        
    if not current_user.check_password(old_password):
        return jsonify({'message': '原密码错误'}), 401
        
    current_user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': '密码修改成功'})

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')
    new_password = data.get('new_password')
    
    if not email or not code or not new_password:
        return jsonify({'message': '请填写完整信息'}), 400
        
    if verification_codes.get(email) != code:
        return jsonify({'message': '验证码错误'}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': '用户不存在'}), 404
        
    user.set_password(new_password)
    db.session.commit()
    
    # Cleanup code
    if email in verification_codes:
        del verification_codes[email]
        
    return jsonify({'message': '密码重置成功，请重新登录'})

# Canvas Management Routes

@app.route('/api/canvases', methods=['GET'])
@token_required
def list_canvases(current_user):
    canvases = Canvas.query.filter_by(owner_id=current_user.id).order_by(Canvas.updated_at.desc()).all()
    # Also find visited/shared canvases (TODO: Implement visited history)
    
    return jsonify({
        'canvases': [{
            'id': c.id,
            'title': c.title,
            'updated_at': c.updated_at,
            'is_public': c.is_public,
            'has_password': bool(c.password_hash)
        } for c in canvases]
    })

@app.route('/api/canvases', methods=['POST'])
@token_required
def create_canvas(current_user):
    data = request.get_json()
    title = data.get('title', '未命名画布')
    
    new_canvas = Canvas(
        owner_id=current_user.id,
        title=title,
        content='{"nodes":[], "edges":[], "viewport": {"x":0, "y":0, "zoom":1}}'
    )
    db.session.add(new_canvas)
    db.session.commit()
    
    return jsonify({'id': new_canvas.id, 'message': '创建成功'})

@app.route('/api/canvases/<canvas_id>/duplicate', methods=['POST'])
@token_required
def duplicate_canvas(current_user, canvas_id):
    source_canvas = Canvas.query.get(canvas_id)
    if not source_canvas:
        return jsonify({'message': '画布不存在'}), 404
        
    # Check permissions: currently only allow owner or if public
    has_access = False
    if source_canvas.owner_id == current_user.id:
        has_access = True
    elif source_canvas.is_public:
        # For simplicity, if it's public (and maybe password protected), we might need checks.
        # But usually duplicate comes from dashboard where you own it.
        # If we allow "forking" public canvases, we need password check.
        # For now, let's assume dashboard usage (own canvases).
        has_access = True
            
    if not has_access:
        return jsonify({'message': '无权访问'}), 403

    new_canvas = Canvas(
        owner_id=current_user.id,
        title=f"{source_canvas.title} (副本)",
        content=source_canvas.content,
        is_public=False, 
        allow_guest_edit=False,
        password_hash=None
    )
    db.session.add(new_canvas)
    db.session.commit()
    
    return jsonify({'id': new_canvas.id, 'message': '复制成功'})

@app.route('/api/canvases/<canvas_id>', methods=['GET'])
def get_canvas(canvas_id):
    current_user = get_current_user_optional()
    canvas = Canvas.query.get(canvas_id)
    
    if not canvas:
        return jsonify({'message': '画布不存在'}), 404
        
    # Check permissions
    has_access = False
    permission = 'read'
    
    if current_user and canvas.owner_id == current_user.id:
        has_access = True
        permission = 'owner'
    elif canvas.is_public:
        # Check password if needed
        auth_token = request.headers.get('X-Canvas-Token')
        password_header = request.headers.get('X-Canvas-Password')
        
        if canvas.password_hash:
            # Check if password provided in header matches
            if password_header and canvas.check_password(password_header):
                pass # Authorized
            elif not auth_token: # Client should send this if they unlocked it
                return jsonify({'message': '需要密码', 'requires_password': True, 'title': canvas.title}), 403
            # If auth_token logic is implemented, verify it here.
            # For now, we rely on X-Canvas-Password for simple protected access.
            
        has_access = True
        if canvas.allow_guest_edit:
            permission = 'edit'
    
    if not has_access:
        return jsonify({'message': '无权访问'}), 403

    response_data = {
        'id': canvas.id,
        'title': canvas.title,
        'owner_id': canvas.owner_id,
        'is_public': canvas.is_public,
        'permission': permission,
        'updated_at': canvas.updated_at,
        'allow_guest_edit': canvas.allow_guest_edit,
        'has_password': bool(canvas.password_hash)
    }
    
    # Check if content is compressed
    content = canvas.content
    if content and content.startswith('GZIP:'):
        # Return as compressed_content, let client decompress
        response_data['compressed_content'] = content[5:] # Remove prefix
    else:
        response_data['content'] = content

    return jsonify(response_data)

@app.route('/api/canvases/<canvas_id>/auth', methods=['POST'])
def canvas_auth(canvas_id):
    data = request.get_json()
    password = data.get('password')
    
    canvas = Canvas.query.get(canvas_id)
    if not canvas:
        return jsonify({'message': '画布不存在'}), 404
        
    if canvas.check_password(password):
        # Generate a temporary token or just tell client it's OK?
        # For simplicity, we return success. Client will store password/state.
        return jsonify({'message': '验证成功', 'success': True})
    
    return jsonify({'message': '密码错误'}), 401

@app.route('/api/canvases/<canvas_id>', methods=['PUT'])
def update_canvas(canvas_id):
    current_user = get_current_user_optional()
    canvas = Canvas.query.get(canvas_id)
    
    if not canvas:
        return jsonify({'message': '画布不存在'}), 404
        
    # Check edit permission
    can_edit = False
    if current_user and canvas.owner_id == current_user.id:
        can_edit = True
    elif canvas.is_public and canvas.allow_guest_edit:
        can_edit = True
        
    if not can_edit:
        return jsonify({'message': '无权编辑'}), 403
        
    data = request.get_json()
    content = data.get('content')
    compressed_content = data.get('compressed_content')
    
    updated = False
    title = data.get('title')
    socket_id = data.get('socket_id')
    
    if title is not None and title != canvas.title:
        canvas.title = title
        updated = True
        
    content_changed = False
    
    if compressed_content:
        # Store compressed content directly, but mark it as compressed?
        # Our DB content column is TEXT (longtext). Base64 string fits fine.
        # But we need to know if it is compressed or not when reading.
        # We can use a prefix or just try to detect.
        # Or better: always store uncompressed for now to keep history/search working?
        # User request: "Directly store compressed data, no decompression on server"
        
        # We will prefix with "GZIP:" to identify compressed content
        new_content = "GZIP:" + compressed_content
        if new_content != canvas.content:
            canvas.content = new_content
            updated = True
            content_changed = True
            
            # We don't have the uncompressed content here to broadcast if we don't decompress.
            # But socketio clients need it. 
            # If we broadcast compressed content, clients need to support it.
            # Our frontend `socket.value.on('canvas_updated')` needs update.
            # Let's broadcast what we received.
            
    elif content and content != canvas.content:
        canvas.content = content
        updated = True
        content_changed = True
        
    if updated:
        # Create history entry only if content changed
        if content_changed:
            new_history = CanvasHistory(
                canvas_id=canvas_id,
                user_id=current_user.id if current_user else None,
                content=canvas.content
            )
            db.session.add(new_history)

        canvas.updated_at = datetime.datetime.utcnow()
        db.session.commit()
        
        # Broadcast update via SocketIO
        emit_data = {
            'title': title,
            'canvas_id': canvas_id,
            'sender_id': socket_id
        }
        
        if compressed_content:
            emit_data['compressed_content'] = compressed_content
        elif content:
            emit_data['content'] = content
            
        socketio.emit('canvas_updated', emit_data, room=canvas_id)
        
    return jsonify({'message': '保存成功'})

@app.route('/api/canvases/<canvas_id>/share', methods=['POST'])
@token_required
def share_canvas(current_user, canvas_id):
    canvas = Canvas.query.get(canvas_id)
    if not canvas or canvas.owner_id != current_user.id:
        return jsonify({'message': '无权操作'}), 403
        
    data = request.get_json()
    canvas.is_public = data.get('is_public', canvas.is_public)
    canvas.allow_guest_edit = data.get('allow_guest_edit', canvas.allow_guest_edit)
    
    password = data.get('password')
    if password is not None: # If explicit null/empty string provided, clear it? Or specific field?
        # Logic: If password provided, set it. If empty string, clear it.
        if password == "":
            canvas.set_password(None)
        else:
            canvas.set_password(password)
            
    db.session.commit()
    return jsonify({'message': '分享设置已更新'})

@app.route('/api/canvases/<canvas_id>', methods=['DELETE'])
@token_required
def delete_canvas(current_user, canvas_id):
    canvas = Canvas.query.get(canvas_id)
    if not canvas or canvas.owner_id != current_user.id:
        return jsonify({'message': '无权操作'}), 403
        
    db.session.delete(canvas)
    db.session.commit()
    return jsonify({'message': '删除成功'})

# Shared Content Routes

@app.route('/api/shares', methods=['POST'])
@token_required
def create_share(current_user):
    data = request.get_json()
    canvas_id = data.get('canvas_id')
    node_ids = data.get('node_ids', []) # List of strings
    settings = data.get('settings', {}) # Dict: {password, allow_edit, etc.}
    
    if not canvas_id:
        return jsonify({'message': 'Canvas ID required'}), 400
        
    canvas = Canvas.query.get(canvas_id)
    if not canvas or canvas.owner_id != current_user.id:
        return jsonify({'message': '无权操作'}), 403
        
    # Handle password hashing in settings if present
    if settings.get('password'):
        settings['password_hash'] = generate_password_hash(settings['password'])
        del settings['password'] # Don't store plain text
        
    new_share = SharedContent(
        canvas_id=canvas_id,
        owner_id=current_user.id,
        node_ids=json.dumps(node_ids),
        settings=json.dumps(settings)
    )
    db.session.add(new_share)
    db.session.commit()
    
    return jsonify({
        'id': new_share.id, 
        'message': '分享链接已创建',
        'url': f"/share/{new_share.id}" # Frontend route
    })

# History Management Routes

@app.route('/api/canvases/<canvas_id>/history', methods=['GET'])
@token_required
def get_canvas_history(current_user, canvas_id):
    canvas = Canvas.query.get(canvas_id)
    if not canvas:
        return jsonify({'message': '画布不存在'}), 404
        
    # Check permissions (Owner or Edit access)
    has_access = False
    if canvas.owner_id == current_user.id:
        has_access = True
    elif canvas.is_public and canvas.allow_guest_edit:
        has_access = True
        
    if not has_access:
        return jsonify({'message': '无权访问'}), 403
        
    # Fetch history
    history = CanvasHistory.query.filter_by(canvas_id=canvas_id).order_by(CanvasHistory.created_at.desc()).limit(50).all()
    
    return jsonify({
        'history': [{
            'id': h.id,
            'created_at': h.created_at,
            'user_id': h.user_id,
            'user_nickname': h.user.nickname if h.user else 'Unknown'
        } for h in history]
    })

@app.route('/api/canvases/<canvas_id>/history', methods=['POST'])
@token_required
def create_canvas_history(current_user, canvas_id):
    canvas = Canvas.query.get(canvas_id)
    if not canvas:
        return jsonify({'message': '画布不存在'}), 404
        
    # Check permissions
    has_access = False
    if canvas.owner_id == current_user.id:
        has_access = True
    elif canvas.is_public and canvas.allow_guest_edit:
        has_access = True
        
    if not has_access:
        return jsonify({'message': '无权操作'}), 403
        
    data = request.get_json()
    content = data.get('content')
    
    if not content:
        return jsonify({'message': '内容为空'}), 400
        
    # Create history entry
    new_history = CanvasHistory(
        canvas_id=canvas_id,
        user_id=current_user.id,
        content=content
    )
    db.session.add(new_history)
    db.session.commit()
    
    return jsonify({'id': new_history.id, 'message': '历史记录已保存'})

@app.route('/api/canvases/<canvas_id>/history/<int:history_id>', methods=['GET'])
@token_required
def get_history_detail(current_user, canvas_id, history_id):
    canvas = Canvas.query.get(canvas_id)
    if not canvas:
        return jsonify({'message': '画布不存在'}), 404
        
    # Check permissions
    has_access = False
    if canvas.owner_id == current_user.id:
        has_access = True
    elif canvas.is_public and canvas.allow_guest_edit:
        has_access = True
        
    if not has_access:
        return jsonify({'message': '无权访问'}), 403
        
    history = CanvasHistory.query.get(history_id)
    if not history or history.canvas_id != canvas_id:
        return jsonify({'message': '记录不存在'}), 404
        
    return jsonify({
        'id': history.id,
        'content': history.content,
        'created_at': history.created_at,
        'user_id': history.user_id
    })

@app.route('/api/canvases/<canvas_id>/history/<int:history_id>/restore', methods=['POST'])
@token_required
def restore_history(current_user, canvas_id, history_id):
    canvas = Canvas.query.get(canvas_id)
    if not canvas:
        return jsonify({'message': '画布不存在'}), 404
        
    # Check permissions (Only owner should restore? Or editors too?)
    # Editors too is fine.
    has_access = False
    if canvas.owner_id == current_user.id:
        has_access = True
    elif canvas.is_public and canvas.allow_guest_edit:
        has_access = True
        
    if not has_access:
        return jsonify({'message': '无权操作'}), 403
        
    history = CanvasHistory.query.get(history_id)
    if not history or history.canvas_id != canvas_id:
        return jsonify({'message': '记录不存在'}), 404
        
    # Update canvas content
    canvas.content = history.content
    canvas.updated_at = datetime.datetime.utcnow()
    db.session.commit()
    
    # Broadcast update
    socketio.emit('canvas_updated', {
        'content': history.content, 
        'title': canvas.title,
        'canvas_id': canvas_id,
        'sender_id': 'system' # System restore
    }, room=canvas_id)
    
    return jsonify({'message': '回滚成功'})

@app.route('/api/shares/<share_id>', methods=['GET'])
def get_share(share_id):
    share = SharedContent.query.get(share_id)
    if not share:
        return jsonify({'message': '分享不存在'}), 404
        
    settings = json.loads(share.settings)
    
    # Check password if needed
    auth_token = request.headers.get('X-Share-Token')
    password_header = request.headers.get('X-Share-Password')
    
    if settings.get('password_hash'):
        if password_header and check_password_hash(settings['password_hash'], password_header):
            pass # Authorized
        elif not auth_token: # Token logic can be added later
             return jsonify({'message': '需要密码', 'requires_password': True, 'title': 'Shared Content'}), 403

    # Construct content subset
    canvas = Canvas.query.get(share.canvas_id)
    if not canvas:
         return jsonify({'message': '原画布已不存在'}), 404
         
    try:
        full_content = json.loads(canvas.content)
        target_node_ids = set(json.loads(share.node_ids))
        
        filtered_nodes = [n for n in full_content.get('nodes', []) if n.get('id') in target_node_ids]
        filtered_edges = [e for e in full_content.get('edges', []) if e.get('source') in target_node_ids and e.get('target') in target_node_ids]
        
        partial_content = {
            'nodes': filtered_nodes,
            'edges': filtered_edges,
            'viewport': full_content.get('viewport', {'x':0, 'y':0, 'zoom':1})
        }
        
        return jsonify({
            'id': share.id,
            'canvas_id': share.canvas_id,
            'content': json.dumps(partial_content),
            'owner_id': share.owner_id,
            'allow_guest_edit': settings.get('allow_edit', False),
            'is_shared_view': True
        })
    except Exception as e:
        print(f"Error parsing canvas content: {e}")
        return jsonify({'message': '内容解析错误'}), 500

@app.route('/api/shares/<share_id>', methods=['PUT'])
def update_share(share_id):
    share = SharedContent.query.get(share_id)
    if not share:
        return jsonify({'message': '分享不存在'}), 404
        
    settings = json.loads(share.settings)
    
    # Check permission
    if not settings.get('allow_edit'):
        return jsonify({'message': '无权编辑'}), 403
        
    # Check password
    password_header = request.headers.get('X-Share-Password')
    if settings.get('password_hash'):
        if not password_header or not check_password_hash(settings['password_hash'], password_header):
            return jsonify({'message': '密码错误或缺失'}), 401

    data = request.get_json()
    content = data.get('content')
    if not content:
        return jsonify({'message': '内容不能为空'}), 400
        
    try:
        # Load original canvas
        canvas = Canvas.query.get(share.canvas_id)
        if not canvas:
            return jsonify({'message': '原画布已不存在'}), 404
            
        # Parse contents
        incoming_content = json.loads(content)
        incoming_nodes = incoming_content.get('nodes', [])
        incoming_edges = incoming_content.get('edges', [])
        
        full_content = json.loads(canvas.content)
        full_nodes = full_content.get('nodes', [])
        full_edges = full_content.get('edges', [])
        
        current_share_node_ids = set(json.loads(share.node_ids))
        
        # Strategy:
        # 1. Update nodes that are in the share
        # 2. Add new nodes if they are meant to be part of the share (assumed yes for now)
        # 3. Handle deletions (if a node was in share but not in incoming)
        
        incoming_node_map = {n['id']: n for n in incoming_nodes}
        full_node_map = {n['id']: n for n in full_nodes}
        
        # Identify nodes to remove from share (and canvas)
        # If a node ID is in current_share_node_ids BUT NOT in incoming_node_map, it was deleted by the user
        nodes_to_remove = []
        for nid in current_share_node_ids:
            if nid not in incoming_node_map:
                nodes_to_remove.append(nid)
                if nid in full_node_map:
                    del full_node_map[nid]
                    
        # Identify nodes to add/update
        # Any node in incoming_nodes is either an update to existing share node, or a new node
        new_share_node_ids = set()
        
        for nid, node in incoming_node_map.items():
            full_node_map[nid] = node
            new_share_node_ids.add(nid)
            
        # Update edges
        # We replace edges that connect share nodes? Or just merge?
        # Simpler: Filter out edges related to share nodes from full list, then add incoming edges
        # But edges might connect to nodes OUTSIDE the share?
        # If edge source/target is in share, we control it?
        # Let's try to just update edges that are fully contained in the share or connected to it.
        # Actually, incoming_edges only contains edges relevant to the share view.
        # Let's merge edges carefully.
        
        incoming_edge_map = {e['id']: e for e in incoming_edges}
        full_edge_map = {e['id']: e for e in full_edges}
        
        # Remove edges that were in the share view but now deleted
        # How do we know which edges "belong" to the share?
        # Maybe we don't strictly enforce edge ownership for now, just update/add.
        # But if user deletes an edge, we need to delete it from canvas.
        # If we only have partial edges, we can't blindly replace.
        
        # Robust Edge Strategy:
        # 1. Keep edges that are NOT touching any shared nodes (preserve context)
        # 2. For edges touching shared nodes, use the incoming list?
        # No, because incoming list might not have edges connecting to outside nodes.
        # Wait, if we are in shared view, we only see subset.
        # If I delete an edge in shared view, I want it gone.
        
        # Let's trust the incoming edges for any edge where BOTH source and target are in the new_share_node_ids.
        # For edges connecting inside-outside, we should preserve them unless explicitly deleted?
        # But the frontend doesn't send "deleted" events, just the new state.
        # If I delete a node, its edges are gone.
        
        # Let's simplify: 
        # Update all nodes as planned.
        # For edges: 
        #   Remove any edge in full_content where source OR target is in nodes_to_remove.
        #   Update/Add any edge in incoming_edges.
        
        # Remove deleted nodes' edges
        final_edges = []
        for e in full_edges:
            if e['source'] in nodes_to_remove or e['target'] in nodes_to_remove:
                continue
            # If edge is in incoming, we'll take the incoming version later
            if e['id'] in incoming_edge_map:
                continue
            final_edges.append(e)
            
        # Add incoming edges
        for e in incoming_edges:
            final_edges.append(e)
            
        # Reconstruct Content
        new_full_content = {
            'nodes': list(full_node_map.values()),
            'edges': final_edges,
            'viewport': full_content.get('viewport') # Preserve original viewport? Or update? Maybe preserve.
        }
        
        canvas.content = json.dumps(new_full_content)
        canvas.updated_at = datetime.datetime.utcnow()
        
        # Update Share Node IDs
        share.node_ids = json.dumps(list(new_share_node_ids))
        
        db.session.commit()
        
        # Broadcast
        socket_id = data.get('socket_id')
        socketio.emit('canvas_updated', {
            'content': json.dumps(new_full_content),
            'canvas_id': share.canvas_id,
            'sender_id': socket_id
        }, room=share.canvas_id)
        
        return jsonify({'message': '保存成功'})
        
    except Exception as e:
        print(f"Error updating shared content: {e}")
        return jsonify({'message': '保存失败', 'error': str(e)}), 500

@app.route('/api/shares/<share_id>/auth', methods=['POST'])
def share_auth(share_id):
    data = request.get_json()
    password = data.get('password')
    
    share = SharedContent.query.get(share_id)
    if not share:
        return jsonify({'message': '分享不存在'}), 404
        
    settings = json.loads(share.settings)
    if not settings.get('password_hash'):
        return jsonify({'success': True})
        
    if check_password_hash(settings['password_hash'], password):
        return jsonify({'success': True})
        
    return jsonify({'message': '密码错误'}), 401

@app.route('/api/my-shares', methods=['GET'])
@token_required
def list_my_shares(current_user):
    shares = SharedContent.query.filter_by(owner_id=current_user.id).order_by(SharedContent.created_at.desc()).all()
    
    result = []
    for s in shares:
        canvas = Canvas.query.get(s.canvas_id)
        canvas_title = canvas.title if canvas else "Unknown Canvas"
        node_count = len(json.loads(s.node_ids))
        settings = json.loads(s.settings)
        
        result.append({
            'id': s.id,
            'canvas_title': canvas_title,
            'node_count': node_count,
            'created_at': s.created_at,
            'has_password': bool(settings.get('password_hash')),
            'allow_edit': settings.get('allow_edit', False)
        })
        
    return jsonify({'shares': result})

@app.route('/api/shares/<share_id>', methods=['DELETE'])
@token_required
def delete_share(current_user, share_id):
    share = SharedContent.query.get(share_id)
    if not share or share.owner_id != current_user.id:
        return jsonify({'message': '无权操作'}), 403
        
    db.session.delete(share)
    db.session.commit()
    return jsonify({'message': '删除成功'})

# Deprecated / Backward Compatibility Routes
@app.route('/api/canvas', methods=['POST'])
@token_required
def save_canvas_legacy(current_user):
    # Find latest canvas or create one
    canvas = Canvas.query.filter_by(owner_id=current_user.id).order_by(Canvas.updated_at.desc()).first()
    if not canvas:
        canvas = Canvas(owner_id=current_user.id, title="我的画布")
        db.session.add(canvas)
    
    data = request.get_json()
    content = data.get('content')
    if content:
        canvas.content = content
        canvas.updated_at = datetime.datetime.utcnow()
        db.session.commit()
    return jsonify({'message': 'Canvas saved successfully'})

@app.route('/api/canvas', methods=['GET'])
@token_required
def load_canvas_legacy(current_user):
    canvas = Canvas.query.filter_by(owner_id=current_user.id).order_by(Canvas.updated_at.desc()).first()
    if not canvas:
        # Try migration from CanvasData
        old_data = CanvasData.query.filter_by(user_id=current_user.id).first()
        if old_data:
            canvas = Canvas(owner_id=current_user.id, title="迁移画布", content=old_data.content)
            db.session.add(canvas)
            db.session.commit()
    
    if canvas:
        return jsonify({'content': canvas.content})
    return jsonify({'content': None})

# WebSocket Events
@socketio.on('join')
def on_join(data):
    username = data.get('username', 'Guest')
    canvas_id = data.get('canvas_id')
    if not canvas_id:
        return
    join_room(canvas_id)
    
    if canvas_id not in room_users:
        room_users[canvas_id] = []
    
    # Check if user already in list (by socket id)
    # If exists, update info (e.g. nickname/avatar change)
    existing_idx = next((i for i, u in enumerate(room_users[canvas_id]) if u['id'] == request.sid), -1)
    
    user_info = {
        'id': request.sid,
        'username': username,
        'color': data.get('color', '#000000'),
        'avatar': data.get('avatar')
    }
    
    if existing_idx >= 0:
        room_users[canvas_id][existing_idx] = user_info
    else:
        room_users[canvas_id].append(user_info)
    
    emit('user_joined', {'users': room_users[canvas_id]}, room=canvas_id)

@socketio.on('leave')
def on_leave(data):
    canvas_id = data.get('canvas_id')
    leave_room(canvas_id)
    if canvas_id in room_users:
        room_users[canvas_id] = [u for u in room_users[canvas_id] if u['id'] != request.sid]
        emit('user_left', {'users': room_users[canvas_id]}, room=canvas_id)

@socketio.on('disconnect')
def on_disconnect():
    for canvas_id, users in room_users.items():
        original_len = len(users)
        room_users[canvas_id] = [u for u in users if u['id'] != request.sid]
        if len(room_users[canvas_id]) < original_len:
            emit('user_left', {'users': room_users[canvas_id]}, room=canvas_id)

@socketio.on('update_canvas')
def on_update_canvas(data):
    canvas_id = data.get('canvas_id')
    content = data.get('content')
    # Broadcast to others
    # Client expects 'sender_id' to filter out own messages if echoed, 
    # but include_self=False handles it on server side usually.
    # However, client logic checks data.sender_id === socket.value.id.
    # So we must send sender_id.
    emit('canvas_updated', {
        'content': content, 
        'canvas_id': canvas_id, 
        'sender_id': request.sid
    }, room=canvas_id, include_self=False)

@socketio.on('update_node')
def on_update_node(data):
    canvas_id = data.get('canvas_id')
    # Broadcast to others in the room
    emit('node_updated', data, room=canvas_id, include_self=False)

@socketio.on('cursor_move')
def on_cursor_move(data):
    canvas_id = data.get('canvas_id')
    emit('cursor_moved', data, room=canvas_id, include_self=False)

@app.route('/api/uploads/<path:filename>')
def serve_file(filename):
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
        
    if file:
        filename = secure_filename(file.filename)
        if not filename:
            filename = 'unnamed_file'
            
        # Add timestamp to filename to prevent duplicates
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}{ext}"
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        
        # Return the full URL or relative path
        file_url = f"http://localhost:5001/api/uploads/{unique_filename}"
        return jsonify({'url': file_url, 'filename': unique_filename})

@app.route('/api/fetch-metadata', methods=['POST'])
def fetch_metadata():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'message': 'URL is required'}), 400
        
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string if soup.title else url
        description = ""
        image = ""
        
        # Try to get description
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        if meta_desc:
            description = meta_desc.get('content', '')
            
        # Try to get image (OG Image)
        meta_image = soup.find('meta', attrs={'property': 'og:image'})
        if meta_image:
            image = meta_image.get('content', '')
            # Handle relative URLs
            if image and not image.startswith('http'):
                from urllib.parse import urljoin
                image = urljoin(url, image)
                
        return jsonify({
            'title': title,
            'description': description,
            'image': image,
            'url': url
        })
        
    except Exception as e:
        print(f"Error fetching metadata: {e}")
        return jsonify({
            'title': url,
            'description': '无法获取网站信息',
            'image': '',
            'url': url,
            'error': str(e)
        })

@app.route('/api/execute', methods=['POST'])
def execute_code():
    data = request.get_json()
    code = data.get('code')
    language = data.get('language')
    
    if not code or not language:
        return jsonify({'message': '代码或语言不能为空'}), 400
        
    language = language.lower()
    
    # Supported languages map to execution details
    # (suffix, command list generator)
    lang_config = {
        'python': ('.py', lambda path: ['python3', path]),
        'py': ('.py', lambda path: ['python3', path]),
        'javascript': ('.js', lambda path: ['node', path]),
        'js': ('.js', lambda path: ['node', path]),
        'nodejs': ('.js', lambda path: ['node', path]),
        'lua': ('.lua', lambda path: ['lua', path]),
        'java': ('.java', lambda path: ['java', path]), # Single file source code execution (Java 11+)
    }
    
    if language not in lang_config:
        return jsonify({'message': f'本地运行暂不支持该语言: {language}'}), 400
        
    suffix, cmd_gen = lang_config[language]
        
    try:
        # Create a temporary file
        # For Java, the class name must match filename if public, but we can't easily parse that.
        # Java 11+ supports running single file source code directly without compilation step if we don't declare public class with different name.
        # But `java temp.java` works if class is not public or matches.
        # We'll use a generic name.
        
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            f.write(code)
            temp_path = f.name
            
        try:
            cmd = cmd_gen(temp_path)
            
            # Check if runtime exists
            try:
                subprocess.run([cmd[0], '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            except FileNotFoundError:
                 return jsonify({'message': f'服务端未安装运行环境: {cmd[0]}' }), 500

            # Run with timeout
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=10 # 10 seconds timeout
            )
            
            output = result.stdout
            if result.stderr:
                # Some languages output to stderr even for non-errors, but usually it's mixed.
                # We append it.
                if output:
                    output += '\n'
                output += result.stderr
                
            return jsonify({
                'result': output, 
                'exit_code': result.returncode
            })
            
        except subprocess.TimeoutExpired:
            return jsonify({
                'result': 'Execution timed out (10s limit)',
                'exit_code': 124
            })
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except Exception as e:
        print(f"Execution error: {e}")
        return jsonify({'message': f'执行出错: {str(e)}'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # socketio.run(app, debug=True, port=5001)
    # Allow 0.0.0.0 for external access
    socketio.run(app, debug=True, port=5001, host='0.0.0.0', allow_unsafe_werkzeug=True)
