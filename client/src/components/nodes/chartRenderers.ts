import * as echarts from 'echarts'

export const ganttRenderItem = (params: any, api: any) => {
  const categoryIndex = api.value(0)
  const start = api.coord([api.value(1), categoryIndex])
  const end = api.coord([api.value(2), categoryIndex])
  const height = api.size([0, 1])[1] * 0.6
  
  const rectShape = echarts.graphic.clipRectByRect(
    {
      x: start[0],
      y: start[1] - height / 2,
      width: end[0] - start[0],
      height: height
    },
    {
      x: params.coordSys.x,
      y: params.coordSys.y,
      width: params.coordSys.width,
      height: params.coordSys.height
    }
  )
  
  return (
    rectShape && {
      type: 'rect',
      transition: ['shape'],
      shape: rectShape,
      style: api.style()
    }
  )
}

export const renderers: Record<string, any> = {
  'ganttRender': ganttRenderItem
}

export const processOption = (option: any) => {
  if (!option || typeof option !== 'object') return option
  
  const newOption = { ...option }
  
  if (newOption.series) {
    newOption.series = newOption.series.map((series: any) => {
      if (series.renderItem && typeof series.renderItem === 'string' && renderers[series.renderItem]) {
        return {
          ...series,
          renderItem: renderers[series.renderItem]
        }
      }
      return series
    })
  }
  
  // Handle tooltip formatter if it's a known string key (future extension)
  
  return newOption
}
