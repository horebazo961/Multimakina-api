import axios, { AxiosError, AxiosInstance } from "axios"

export type Vehicle = {
  id: number
  brand: string
  model: string
  vin: string
  internal_code?: string | null
  category?: string
  status?: string
  maintenance_type?: string
  taller_propietario?: string
  dtc_codes?: string | null
}

export type VehiclePayload = {
  brand?: string
  model?: string
  vin?: string
  internal_code?: string
  category?: string
  status?: string
  maintenance_type?: string
  taller_propietario?: string
  escuderia?: string
}

export const FLEET_STATUSES = [
  "En box",
  "En preparación",
  "Listo para pista",
  "En pista",
  "Fuera de servicio",
] as const

export const FLEET_CATEGORIES = ["Rental", "Competición", "Escuela", "Otro"] as const

export const MAINTENANCE_TYPES = [
  "Preventivo",
  "Correctivo",
  "Diagnóstico Electrónico",
  "Setup de carrera",
] as const

const baseURL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "")
const writeKey = (process.env.NEXT_PUBLIC_API_WRITE_KEY || "").trim()

export const api: AxiosInstance = axios.create({
  baseURL,
  timeout: 45_000,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
    ...(writeKey ? { "X-API-Key": writeKey } : {}),
  },
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
  if (axiosError.response?.status === 401) {
    return "No autorizado para modificar la flota. Revisa la clave de escritura (API key)."
  }
  if (axiosError.code === "ECONNABORTED") {
    return "El backend está tardando. En Render Free puede estar despertando (cold start ~50s)."
  }
  if (!axiosError.response) {
    return "No fue posible conectar con el backend. Verifica NEXT_PUBLIC_API_URL y CORS."
  }
  return "Ocurrió un error al comunicarse con el backend."
}

export async function listVehicles() {
  const { data } = await api.get<Vehicle[]>("/api/v1/vehicles/")
  return data
}

export async function createVehicle(payload: VehiclePayload) {
  const { data } = await api.post<{ message: string; id: number; status?: string; internal_code?: string }>(
    "/api/v1/vehicles/",
    payload,
  )
  return data
}

export async function updateVehicle(id: number, payload: VehiclePayload) {
  const { data } = await api.patch<Vehicle>(`/api/v1/vehicles/${id}`, payload)
  return data
}
