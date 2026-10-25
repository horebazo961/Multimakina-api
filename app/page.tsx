
"use client"

import {
  useCallback,
  useEffect,
  useState,
} from "react"
import type { FormEvent } from "react"

import {
  Activity,
  AlertTriangle,
  CarFront,
  CheckCircle2,
  Clock3,
  Database,
  Gauge,
  RefreshCw,
  Server,
  ShieldCheck,
  Wrench,
  Zap,
} from "lucide-react"

import {
  apiErrorCode,
  apiErrorMessage,
  createVehicle,
  listVehicles,
} from "@/lib/api"

import type {
  Vehicle,
  VehiclePayload,
} from "@/lib/api"

const TIME_ZONE = "America/Guayaayaquil".replace(
  "Guayaayaquil",
  "Guayaquil"
)

const INITIAL_FORM = {
  brand: "",
  model: "",
  vin: "",
  maintenance_type: "Diagnóstico Electrónico",
  taller_propietario: "",
}

function formatDateTime(value: string | Date): string {
  const date = value instanceof Date
    ? value
    : new Date(value)

  if (Number.isNaN(date.getTime())) {
    return "Fecha no disponible"
  }

  return new Intl.DateTimeFormat("es-EC", {
    timeZone: TIME_ZONE,
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date)
}

function statusTone(status?: string | null): string {
  const value = (status || "").toLocaleLowerCase("es")

  if (
    value.includes("operativo") ||
    value.includes("completado")
  ) {
    return "status-good"
  }

  if (
    value.includes("error") ||
    value.includes("fall") ||
    value.includes("crítico") ||
    value.includes("critico")
  ) {
    return "status-danger"
  }

  if (
    value.includes("diagnóstico") ||
    value.includes("diagnostico") ||
    value.includes("pendiente") ||
    value.includes("mantenimiento")
  ) {
    return "status-warn"
  }

  return "status-neutral"
}

function displayValue(value?: string | null): string {
  return value?.trim() || "No especificado"
}

function displayDtcCodes(
  value?: string | string[] | null
): string {
  if (Array.isArray(value)) {
    return value.length > 0
      ? value.join(", ")
      : "Sin datos reportados"
  }

  return value?.trim() || "Sin datos reportados"
}

function isFollowUpStatus(status?: string | null): boolean {
  const value = (status || "").toLocaleLowerCase("es")

  return [
    "diagnóstico",
    "diagnostico",
    "pendiente",
    "mantenimiento",
  ].some((keyword) => value.includes(keyword))
}

export default function DashboardPage() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [form, setForm] = useState(INITIAL_FORM)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")
  const [vinError, setVinError] = useState("")
  const [success, setSuccess] = useState("")
  const [lastSync, setLastSync] = useState<Date | null>(null)
  const [now, setNow] = useState<Date | null>(null)

  const refresh = useCallback(async () => {
    setLoading(true)

    try {
      const data = await listVehicles()

      setVehicles(data)
      setLastSync(new Date())
      setError("")
    } catch (err) {
      setError(apiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    setNow(new Date())

    const clockTimer = window.setInterval(() => {
      setNow(new Date())
    }, 1000)

    void refresh()

    const syncTimer = window.setInterval(() => {
      if (!document.hidden) {
        void refresh()
      }
    }, 15000)

    return () => {
      window.clearInterval(clockTimer)
      window.clearInterval(syncTimer)
    }
  }, [refresh])

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault()

    setSaving(true)
    setError("")
    setVinError("")
    setSuccess("")

    const normalizedVin = form.vin.trim().toUpperCase()

    if (!/^[A-HJ-NPR-Z0-9]{17}$/.test(normalizedVin)) {
      setVinError(
        "Introduce un VIN de 17 caracteres válidos. " +
        "Las letras I, O y Q no se utilizan en el VIN estándar."
      )
      setSaving(false)
      return
    }

    const payload: VehiclePayload = {
      brand: form.brand.trim(),
      model: form.model.trim(),
      vin: normalizedVin,
      maintenance_type: form.maintenance_type,
      taller_propietario: form.taller_propietario.trim(),
      status: "Diagnóstico",
    }

    try {
      await createVehicle(payload)

      setForm(INITIAL_FORM)
      setSuccess(
        "El servidor aceptó la solicitud. " +
        "Actualizando la lista de vehículos."
      )

      await refresh()
    } catch (err) {
      const code = apiErrorCode(err)
      const message = apiErrorMessage(err)

      if (
        code === "DUPLICATE_VIN" ||
        code === "VIN_ALREADY_EXISTS"
      ) {
        setVinError(message)
      } else {
        setError(message)
      }
    } finally {
      setSaving(false)
    }
  }

  const followUpCount = vehicles.filter(
    (vehicle) => isFollowUpStatus(vehicle.status)
  ).length

  const latestSyncTime = lastSync
    ? new Intl.DateTimeFormat("es-EC", {
        timeZone: TIME_ZONE,
        hour: "2-digit",
        minute: "2-digit",
      }).format(lastSync)
    : "—"

  return (
    <main className="app-shell">
      <div className="ambient ambient-one" aria-hidden="true" />
      <div className="ambient ambient-two" aria-hidden="true" />

      <div className="dashboard">
        <header className="topbar">
          <a
            href="#inicio"
            className="brand"
            aria-label="MULTIMAKINA, inicio"
          >
            <span className="brand-mark">
              <Gauge size={22} strokeWidth={2.2} />
            </span>

            <span className="brand-copy">
              <span className="brand-name">
                MULTIMAKINA<span className="brand-dot">.</span>
              </span>

              <span className="brand-subtitle">
                AUTOMOTIVE INTELLIGENCE
              </span>
            </span>
          </a>

          <div className="topbar-right">
            <span
              className={[
                "connection-pill",
                error
                  ? "connection-offline"
                  : lastSync
                    ? "connection-online"
                    : "connection-pending",
              ].join(" ")}
            >
              <span className="connection-dot" />

              {error
                ? "Conexión con incidencias"
                : lastSync
                  ? "API conectada"
                  : "Conectando API"}
            </span>

            <div className="clock-block">
              <Clock3 size={16} />

              <span>
                {now
                  ? formatDateTime(now)
                  : "Cargando hora…"}
              </span>

              <span className="timezone">ECU</span>
            </div>
          </div>
        </header>

        <section id="inicio" className="hero">
          <div>
            <p className="eyebrow">
              <span className="eyebrow-line" />
              CENTRO DE OPERACIONES
            </p>

            <h1>
              Control de <span>flota.</span>
            </h1>

            <p className="hero-description">
              Vehículos, mantenimientos y datos operativos
              en un solo lugar.
            </p>
          </div>

          <button
            type="button"
            onClick={() => void refresh()}
            disabled={loading}
            className="button-secondary refresh-button"
          >
            <RefreshCw
              size={16}
              className={loading ? "spin" : ""}
            />
            Sincronizar
          </button>
        </section>

        <section
          className="metrics-grid"
          aria-label="Resumen de la flota"
        >
          <article className="metric-card">
            <div className="metric-top">
              <span>Vehículos registrados</span>
              <span className="metric-icon">
                <CarFront size={18} />
              </span>
            </div>

            <div className="metric-value">
              {loading && vehicles.length === 0
                ? "—"
                : vehicles.length.toLocaleString("es-EC")}
            </div>

            <div className="metric-foot">
              Registros devueltos por la API
            </div>
          </article>

          <article className="metric-card">
            <div className="metric-top">
              <span>En seguimiento</span>
              <span className="metric-icon">
                <Activity size={18} />
              </span>
            </div>

            <div className="metric-value">
              {loading && vehicles.length === 0
                ? "—"
                : followUpCount.toLocaleString("es-EC")}
            </div>

            <div className="metric-foot">
              Según el estado reportado
            </div>
          </article>

          <article className="metric-card">
            <div className="metric-top">
              <span>Última sincronización</span>
              <span className="metric-icon">
                <Database size={18} />
              </span>
            </div>

            <div className="metric-value metric-value-small">
              {latestSyncTime}
            </div>

            <div className="metric-foot">
              {lastSync
                ? formatDateTime(lastSync)
                : "Aún sin confirmar"}
            </div>
          </article>

          <article className="metric-card">
            <div className="metric-top">
              <span>Telemetría</span>
              <span className="metric-icon">
                <Zap size={18} />
              </span>
            </div>

            <div className="metric-value metric-value-small">
              Sin señal
            </div>

            <div className="metric-foot">
              No hay lecturas en vivo conectadas
            </div>
          </article>
        </section>

        <section className="content-grid">
          <section
            className="surface register-panel"
            aria-labelledby="register-title"
          >
            <div className="section-heading">
              <div className="section-icon">
                <CarFront size={19} />
              </div>

              <div>
                <p className="eyebrow">NUEVO REGISTRO</p>
                <h2 id="register-title">
                  Ingresar vehículo
                </h2>
              </div>
            </div>

            <p className="section-description">
              Completa los datos básicos. El backend debe
              validar y guardar el registro.
            </p>

            <form
              onSubmit={handleSubmit}
              className="vehicle-form"
            >
              <label className="field">
                <span>
                  Marca<span className="required-mark"> *</span>
                </span>

                <input
                  required
                  minLength={1}
                  maxLength={80}
                  value={form.brand}
                  onChange={(event) => {
                    setForm((current) => ({
                      ...current,
                      brand: event.target.value,
                    }))
                  }}
                  placeholder="Ej. Toyota"
                  autoComplete="organization"
                />
              </label>

              <label className="field">
                <span>
                  Modelo<span className="required-mark"> *</span>
                </span>

                <input
                  required
                  minLength={1}
                  maxLength={80}
                  value={form.model}
                  onChange={(event) => {
                    setForm((current) => ({
                      ...current,
                      model: event.target.value,
                    }))
                  }}
                  placeholder="Ej. Hilux 2.8"
                  autoComplete="off"
                />
              </label>

              <label className="field">
                <span>
                  VIN / chasis
                  <span className="required-mark"> *</span>
                </span>

                <input
                  required
                  minLength={17}
                  maxLength={17}
                  pattern="[A-HJ-NPR-Z0-9]{17}"
                  value={form.vin}
                  onChange={(event) => {
                    setForm((current) => ({
                      ...current,
                      vin: event.target.value.toUpperCase(),
                    }))

                    setVinError("")
                  }}
                  aria-invalid={Boolean(vinError)}
                  aria-describedby={
                    vinError ? "vin-error" : undefined
                  }
                  placeholder="17 caracteres"
                  autoComplete="off"
                  spellCheck={false}
                />

                {vinError && (
                  <span
                    id="vin-error"
                    className="field-error"
                    role="alert"
                  >
                    {vinError}
                  </span>
                )}
              </label>

              <label className="field">
                <span>Tipo de mantenimiento</span>

                <select
                  value={form.maintenance_type}
                  onChange={(event) => {
                    setForm((current) => ({
                      ...current,
                      maintenance_type: event.target.value,
                    }))
                  }}
                >
                  <option>Diagnóstico Electrónico</option>
                  <option>Preventivo</option>
                  <option>Correctivo</option>
                  <option>Inspección general</option>
                </select>
              </label>

              <label className="field">
                <span>Taller / propietario</span>

                <input
                  maxLength={120}
                  value={form.taller_propietario}
                  onChange={(event) => {
                    setForm((current) => ({
                      ...current,
                      taller_propietario: event.target.value,
                    }))
                  }}
                  placeholder="Nombre del taller (opcional)"
                  autoComplete="organization"
                />
              </label>

              {error && (
                <div role="alert" className="notice notice-error">
                  <AlertTriangle size={17} />
                  <span>{error}</span>
                </div>
              )}

              {success && (
                <div role="status" className="notice notice-success">
                  <CheckCircle2 size={17} />
                  <span>{success}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={saving}
                className="button-primary"
              >
                {saving
                  ? <RefreshCw size={16} className="spin" />
                  : <Zap size={16} />}

                {saving
                  ? "Enviando registro…"
                  : "Registrar vehículo"}
              </button>

              <p className="form-footnote">
                <ShieldCheck size={14} />
                La confirmación depende de la respuesta del servidor.
              </p>
            </form>
          </section>

          <section
            className="surface fleet-panel"
            aria-labelledby="fleet-title"
          >
            <div className="fleet-heading">
              <div>
                <p className="eyebrow">
                  INVENTARIO OPERATIVO
                </p>

                <h2 id="fleet-title">
                  Vehículos ingresados
                </h2>

                <p className="section-description">
                  Vista resumida de los registros disponibles.
                </p>
              </div>

              <span className="count-chip">
                {vehicles.length}{" "}
                {vehicles.length === 1 ? "unidad" : "unidades"}
              </span>
            </div>

            {error && (
              <div
                role="alert"
                className="notice notice-error fleet-notice"
              >
                <AlertTriangle size={17} />

                <span>
                  No se pudo actualizar la flota. {error}
                  {" "}Los datos anteriores, si existen,
                  se conservan en pantalla.
                </span>
              </div>
            )}

            {loading && vehicles.length === 0 ? (
              <div className="empty-state">
                <RefreshCw size={22} className="spin" />
                <p>Consultando registros…</p>
                <span>
                  Esperando respuesta del backend
                </span>
              </div>
            ) : vehicles.length === 0 ? (
              <div className="empty-state">
                <CarFront size={25} />
                <p>Aún no hay vehículos registrados</p>
                <span>
                  Cuando la API devuelva registros,
                  aparecerán aquí como tarjetas.
                </span>
              </div>
            ) : (
              <div className="vehicle-grid">
                {vehicles.map((vehicle) => (
                  <article
                    className="vehicle-card"
                    key={vehicle.id}
                  >
                    <div className="vehicle-card-top">
                      <span className="vehicle-icon">
                        <CarFront size={20} />
                      </span>

                      <span
                        className={[
                          "status-chip",
                          statusTone(vehicle.status),
                        ].join(" ")}
                      >
                        {vehicle.status || "Estado no reportado"}
                      </span>
                    </div>

                    <h3>
                      {vehicle.brand}{" "}
                      <span>{vehicle.model}</span>
                    </h3>

                    <p className="vehicle-vin">
                      VIN · {vehicle.vin || "No disponible"}
                    </p>

                    <div className="vehicle-details">
                      <div className="detail-row">
                        <Wrench size={14} />
                        <span>Mantenimiento</span>
                        <strong>
                          {displayValue(vehicle.maintenance_type)}
                        </strong>
                      </div>

                      <div className="detail-row">
                        <Activity size={14} />
                        <span>Códigos DTC</span>
                        <strong>
                          {displayDtcCodes(vehicle.dtc_codes)}
                        </strong>
                      </div>

                      <div className="detail-row">
                        <Server size={14} />
                        <span>Taller</span>
                        <strong>
                          {displayValue(vehicle.taller_propietario)}
                        </strong>
                      </div>

                      <div className="detail-row">
                        <Clock3 size={14} />
                        <span>Fecha de ingreso</span>
                        <strong>
                          {vehicle.created_at
                            ? formatDateTime(vehicle.created_at)
                            : "No disponible en la API"}
                        </strong>
                      </div>
                    </div>

                    <div className="vehicle-card-footer">
                      <span>Identificador</span>
                      <code>#{vehicle.id}</code>
                    </div>
                  </article>
       