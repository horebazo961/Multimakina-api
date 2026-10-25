import axios, { AxiosError, AxiosInstance } from "axios"

export type Vehicle = {
  id: number
  brand: string
  model: string
  vin: string
  status?: string
  maintenance_type?: string
  taller_propietario?: string
  dtc_codes?: string | null
}

export type VehiclePayload = Omit<Vehicle, "id"> & { id?: number }

const baseURL = (process.env.NEXT_PUBLIC_API_URL || "https://multimakina-api.onrender.com").replace(/\/$/, "")

export const api: AxiosInstance = axios.create({
  baseURL,
  timeout: 45_000,
  headers: { Accept: "application/json", "Content-Type": "application/json" },
})

function isRetryable(error: AxiosError) {
  return !error.response || error.code === "ECONNABORTED" || error.response.status >= 500
}

api.interceptors.response.use(undefined, async (error: AxiosError) => {
  const config = error.config as (typeof error.config & { _retry?: number }) | undefined
  if (config && isRetryable(error) && (config._retry || 0) < 2) {
    config._retry = (config._retry || 0) + 1
    await new Promise((resolve) => setTimeout(resolve, 800 * config._retry!))
    return api(config)
  }
  return Promise.reject(error)
})

export function apiErrorCode(error: unknown) {
  const axiosError = error as AxiosError<{ detail?: { code?: string; message?: string } | string }>
  const detail = axiosError.response?.data?.detail
  return typeof detail === "object" ? detail?.code : undefined
}

export function apiErrorMessage(error: unknown) {
  const axiosError = error as AxiosError<{ detail?: { message?: string } | string }>
  const detail = axiosError.response?.data?.detail
  if (typeof detail === "object" && detail?.message) return detail.message
  if (typeof detail === "string") return detail
  if (axiosError.code === "ECONNABORTED") return "El backend está tardando en despertar. Render puede estar iniciando el servicio."
  if (!axiosError.response) return "No fue posible conectar con Render. Verifica NEXT_PUBLIC_API_URL y CORS."
  return "Ocurrió un error inesperado al comunicarse con el backend."
}

export async function listVehicles() {
  const { data } = await api.get<Vehicle[]>("/vehicles/")
  return data
}

export async function createVehicle(payload: VehiclePayload) {
  const { data } = await api.post<Vehicle>("/vehicles/", payload)
  return data
}
