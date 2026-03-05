export async function uploadFile(file: File): Promise<string> {
  const formData = new FormData()
  formData.append('file', file)
  
  const token = localStorage.getItem('token')
  const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001'}/api/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  })
  
  if (!res.ok) {
    if (res.status === 401) {
      alert('请先登录后上传')
      throw new Error('Unauthorized')
    }
    const errorText = await res.text()
    console.error('Upload failed:', res.status, errorText)
    throw new Error(`Upload failed: ${res.status} ${res.statusText}`)
  }
  
  const data = await res.json()
  return data.url
}
