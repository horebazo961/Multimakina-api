
import axios, {
  AxiosError,
  AxiosInstance,
} from "axios"

export type Vehicle = {
  id: number
  brand: string
  model: string
  vin: string
  status?: string | null
  maintenance_type?: string | null
  taller_propietario?: string | null
  dtc_codes?: string | string[] | null
  created_at?: string | null
}

export type VehiclePayload = {
  brand: string
  model: string
  vin: string
  status?: string
  maintenance_type?: string
  taller_propietario?: string
}

type ApiErrorBody = {
  detail?: string | {
    code?: string
    message?: string
  }
}

type RetryableRequest = {
  _retry?: number
}

const configuredBaseURL =
  process.env.NEXT_PUBLIC_API_URL?.trim().replace(/\/+$/, "")

const isConfigured = Boolean(configuredBaseURL)

export const api: AxiosInstance = axios.create({
  ...(configuredBaseURL
    ? { baseURL: configuredBaseURL }
    : {}),
  timeout: 20_000,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
})

function isRetryableRead(error: AxiosError): boolean {
  const method = (error.config?.method || "get").toLowerCase()

  if (method !== "get") {
    return false
  }

  if (!error.response) {
    return true
  }

  return error.response.status >= 500
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as
      | (typeof error.config & RetryableRequest)
      | undefined

    if (
      config &&
      isRetryableRead(error) &&
      (config._retry || 0) < 2
    ) {
      config._retry = (config._retry || 0) + 1

      await new Promise((resolve) => {
        setTimeout(resolve, 500 * config._retry!)
      })

      return api(config)
    }

    return Promise.reject(error)
  }
)

export function apiErrorCode(error: unknown): string | undefined {
  if (!axios.isAxiosError<ApiErrorBody>(error)) {
    return undefined
  }

  const detail = error.response?.data?.detail

  if (typeof detail === "object" && detail !== null) {
    return detail.code
  }

  return undefined
}

export function apiErrorMessage(error: unknown): string {
  if (!isConfigured) {
    return (
      "La API no está configurada. Define NEXT_PUBLIC_API_URL " +
      "en las variables de entorno del despliegue."
    )
  }

  if (!axios.isAxiosError<ApiErrorBody>(error)) {
    return "No se pudo completar la operación. Intenta nuevamente."
  }

  const status = error.response?.status

  if (error.code === "ECONNABORTED") {
    return "La API tardó demasiado en responder. Intenta sincronizar de nuevo."
  }

  if (!error.response) {
    return (
      "No fue posible conectar con la API. " +
      "Verifica la disponibilidad del servidor y la configuración CORS."
    )
  }

  if (status === 400 || status === 422) {
    return "Los datos enviados no cumplen las validaciones del servidor."
  }

  if (status === 401) {
    return "La sesión o las credenciales no son válidas. Inicia sesión nuevamente."
  }

  if (status === 403) {
    return "No tienes permisos para realizar esta operación."
  }

  if (status === 404) {
    return "El recurso solicitado no está disponible en la API."
  }

  if (status === 409) {
    return "Existe un conflicto con el registro. Comprueba si ya fue ingresado."
  }

  if (status === 429) {
    return "Se han realizado demasiadas solicitudes. Espera antes de reintentar."
  }

  if (status && status >= 500) {
    return (
      "La API encontró un error interno. " +
      "El detalle técnico debe revisarse en los registros del servidor."
    )
  }

  return "La solicitud no pudo completarse. Revisa los datos y los permisos."
}

function ensureApiConfigured(): void {
  if (!isConfigured) {
    throw new Error("API_NOT_CONFIGURED")
  }
}

export async function listVehicles(): Promise<Vehicle[]> {
  ensureApiConfigured()

  const { data } = await api.get<Vehicle[]>(
    "/api/v1/vehicles/"
  )

  if (!Array.isArray(data)) {
    throw new Error("INVALID_VEHICLE_RESPONSE")
  }

  return data
}

export async function createVehicle(
  payload: VehiclePayload
): Promise<Vehicle> {
  ensureApiConfigured()

  const { data } = await api.post<Vehicle>(
    "/api/v1/vehicles/",
    payload
  )

  return data
}
