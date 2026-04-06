import api from './client'

export const fetchCommodityPrices = (materialType) =>
  api.get('/commodity-prices/', { params: { material_type: materialType } })

export const fetchSupportedMaterialTypes = () =>
  api.get('/commodity-prices/supported-types')
