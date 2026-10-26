"use client"

import { FormEvent, useCallback, useEffect, useState } from "react"
import {
  Activity,
  AlertTriangle,
  CarFront,
  CheckCircle2,
  Flag,
  RefreshCw,
  Server,
  Zap,
} from "lucide-react"
import {
  FLEET_CATEGORIES,
  FLEET_STATUSES,
  MAINTENANCE_TYPES,
  apiErrorCode,
  apiErrorMessage,
  createVehicle,
  listVehicles,
  updateVehicle,
  Vehicle,
} from "@/lib/api"

const initialForm = {
  brand: "",
  model: "",
  vin: "",
  internal_code: "",
  category: "Rental",
  status: "En box",
  maintenance_type: "Preventivo",
  taller_propietario: "Kartódromo Quito",
}

export default function DashboardPage() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [form, setForm] = useState(initialForm)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [updatingId, setUpdatingId] = useState<number | null>(null)
  const [error, setError] = useState("")
  const [idError, setIdError] = useState("")
  const [success, setSuccess] = useState("")
  const [lastSync, setLastSync] = useState<Date | null>(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    try {
      setVehicles(await listVehicles())
      setLastSync(new Date())
      setError("")
    } catch (err) {
      setError(apiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
    const interval = window.setInterval(() => {
      if (!document.hidden) refresh()
    }, 15000)
    return () => window.clearInterval(interval)
  }, [refresh])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSaving(true)
    setError("")
    setIdError("")
    setSuccess("")

    const vin = form.vin.trim().toUpperCase()
    const internal_code = form.internal_code.trim().toUpperCase()

    if (!vin && !internal_code) {
      setIdError("Indica código de pista o VIN.")
      setSaving(false)
      return
    }

    try {
      await createVehicle({
        brand: form.brand.trim() || "Sin marca",
        model: form.model.trim() || "Sin modelo",
        vin: vin || undefined,
        internal_code: internal_code || undefined,
        category: form.category,
        status: form.status,
        maintenance_type: form.maintenance_type,
        taller_propietario: form.taller_propietario.trim() || "Kartódromo Quito",
      })
      setSuccess("Unidad registrada en la flota del kartódromo.")
      setForm(initialForm)
      await refresh()
    } catch (err) {
      const code = apiErrorCode(err)
      const message = apiErrorMessage(err)
      if (code === "DUPLICATE_IDENTIFIER" || code === "DUPLICATE_VIN") setIdError(message)
      else setError(message)
    } finally {
      setSaving(false)
    }
  }

  async function handleStatusChange(id: number, status: string) {
    setUpdatingId(id)
    setError("")
    try {
      await updateVehicle(id, { status })
      setVehicles((current) => current.map((v) => (v.id === id ? { ...v, status } : v)))
    } catch (err) {
      setError(apiErrorMessage(err))
    } finally {
      setUpdatingId(null)
    }
  }

  const listos = vehicles.filter((v) => v.status === "Listo para pista").length
  const enBox = vehicles.filter((v) => v.status === "En box" || v.status === "En preparación").length

  return (
    <main className="min-h-screen bg-ink px-5 py-6 text-slate-100 md:px-10">
      <header className="mx-auto flex max-w-7xl items-center justify-between border-b border-line pb-6">
        <div className="flex items-center gap-3">
          <div className="grid size-10 place-items-center rounded-xl bg-signal text-ink">
            <Flag size={20} />
          </div>
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.25em] text-signal">
              Multimakina / kartódromo
            </p>
            <h1 className="text-xl font-extrabold tracking-tight">Control de flota · box y pista</h1>
          </div>
        </div>
        <div className="hidden items-center gap-3 text-xs text-slate-400 sm:flex">
          <span className="flex items-center gap-2">
            <span className="size-2 rounded-full bg-signal" /> API 3.1 · MVP
          </span>
          <span className="rounded-full border border-line px-3 py-1 font-mono">Quito</span>
        </div>
      </header>

      <section className="mx-auto max-w-7xl py-8">
        <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { label: "Unidades en flota", value: vehicles.length, icon: CarFront },
            { label: "En box / preparación", value: enBox, icon: Activity },
            { label: "Listos para pista", value: listos, icon: Flag },
            { label: "Sistema", value: error ? "Revisar" : "Operativo", icon: Server },
          ].map(({ label, value, icon: Icon }) => (
            <article key={label} className="rounded-2xl border border-line bg-panel p-5">
              <div className="mb-5 flex items-center justify-between">
                <p className="text-xs text-slate-400">{label}</p>
                <Icon size={17} className="text-signal" />
              </div>
              <p className="text-2xl font-bold">{value}</p>
            </article>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
          <section className="rounded-2xl border border-line bg-panel p-6">
            <div className="mb-6">
              <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-signal">Nueva unidad</p>
              <h2 className="mt-2 text-lg font-bold">Registrar en flota</h2>
              <p className="mt-1 text-xs leading-5 text-slate-400">
                Código de pista o VIN. Sin datos de pilotos en este MVP.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <label className="block">
                <span className="mb-1.5 block text-xs font-semibold text-slate-300">Código de pista / box</span>
                <input
                  value={form.internal_code}
                  onChange={(e) => {
                    setForm({ ...form, internal_code: e.target.value })
                    setIdError("")
                  }}
                  placeholder="Ej. K-12 / BOX-03"
                  className="w-full rounded-xl border border-line bg-ink px-3.5 py-3 text-sm outline-none focus:border-signal"
                />
              </label>

              <label className="block">
                <span className="mb-1.5 block text-xs font-semibold text-slate-300">VIN (opcional si hay código)</span>
                <input
                  value={form.vin}
                  onChange={(e) => {
                    setForm({ ...form, vin: e.target.value })
                    setIdError("")
                  }}
                  placeholder="Si aplica"
                  className={`w-full rounded-xl border bg-ink px-3.5 py-3 text-sm outline-none focus:border-signal ${
                    idError ? "border-red-400" : "border-line"
                  }`}
                />
                {idError && <span className="mt-1.5 block text-xs text-red-300">{idError}</span>}
              </label>

              <div className="grid grid-cols-2 gap-3">
                <label className="block">
                  <span className="mb-1.5 block text-xs font-semibold text-slate-300">Marca</span>
                  <input
                    value={form.brand}
                    onChange={(e) => setForm({ ...form, brand: e.target.value })}
                    placeholder="Marca"
                    className="w-full rounded-xl border border-line bg-ink px-3.5 py-3 text-sm outline-none focus:border-signal"
                  />
                </label>
                <label className="block">
                  <span className="mb-1.5 block text-xs font-semibold text-slate-300">Modelo</span>
                  <input
                    value={form.model}
                    onChange={(e) => setForm({ ...form, model: e.target.value })}
                    placeholder="Modelo"
                    className="w-full rounded-xl border border-line bg-ink px-3.5 py-3 text-sm outline-none focus:border-signal"
                  />
                </label>
              </div>

              <label className="block">
                <span className="mb-1.5 block text-xs font-semibold text-slate-300">Categoría</span>
                <select
                  value={form.category}
                  onChange={(e) => setForm({ ...form, category: e.target.value })}
                  className="w-full rounded-xl border border-line bg-ink px-3.5 py-3 text-sm outline-none focus:border-signal"
                >
                  {FLEET_CATEGORIES.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </label>

              <label className="block">
                <span className="mb-1.5 block text-xs font-semibold text-slate-300">Estado inicial</span>
                <select
                  value={form.status}
                  onChange={(e) => setForm({ ...form, status: e.target.value })}
                  className="w-full rounded-xl border border-line bg-ink px-3.5 py-3 text-sm outline-none focus:border-signal"
                >
                  {FLEET_STATUSES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </label>

              <label className="block">
                <span className="mb-1.5 block text-xs font-semibold text-slate-300">Tipo de trabajo</span>
                <select
                  value={form.maintenance_type}
                  onChange={(e) => setForm({ ...form, maintenance_type: e.target.value })}
                  className="w-full rounded-xl border border-line bg-ink px-3.5 py-3 text-sm outline-none focus:border-signal"
                >
                  {MAINTENANCE_TYPES.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </label>

              <label className="block">
                <span className="mb-1.5 block text-xs font-semibold text-slate-300">Escudería / taller</span>
                <input
                  value={form.taller_propietario}
                  onChange={(e) => setForm({ ...form, taller_propietario: e.target.value })}
                  placeholder="Kartódromo Quito"
                  className="w-full rounded-xl border border-line bg-ink px-3.5 py-3 text-sm outline-none focus:border-signal"
                />
              </label>

              {error && (
                <div
                  role="alert"
                  className="flex gap-2 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-xs leading-5 text-red-300"
                >
                  <AlertTriangle size={16} className="mt-0.5 shrink-0" />
                  {error}
                </div>
              )}
              {success && (
                <div
                  role="status"
                  className="flex gap-2 rounded-xl border border-signal/30 bg-signal/10 p-3 text-xs leading-5 text-signal"
                >
                  <CheckCircle2 size={16} className="mt-0.5 shrink-0" />
                  {success}
                </div>
              )}

              <button
                disabled={saving}
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-signal py-3 text-sm font-bold text-ink transition hover:bg-emerald-300 disabled:cursor-wait disabled:opacity-60"
              >
                {saving && <RefreshCw size={15} className="animate-spin" />}
                {saving ? "Guardando..." : "Registrar unidad"}
              </button>
            </form>
          </section>

          <section className="min-w-0 rounded-2xl border border-line bg-panel p-6">
            <div className="mb-6 flex items-start justify-between gap-4">
              <div>
                <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-signal">Flota en vivo</p>
                <h2 className="mt-2 text-lg font-bold">Unidades · box y pista</h2>
                <p className="mt-1 text-xs text-slate-400">
                  Auto-sync 15s
                  {lastSync && ` · ${lastSync.toLocaleTimeString("es-EC")}`}
                </p>
              </div>
              <button
                onClick={refresh}
                disabled={loading}
                aria-label="Sincronizar flota"
                className="rounded-xl border border-line p-2.5 text-slate-300 hover:border-signal hover:text-signal"
              >
                <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
              </button>
            </div>

            <div className="overflow-x-auto rounded-xl border border-line">
              <table className="w-full min-w-[720px] text-left text-sm">
                <thead className="bg-ink text-[10px] uppercase tracking-wider text-slate-500">
                  <tr>
                    {["Unidad", "Código", "Categoría", "Escudería", "Estado"].map((h) => (
                      <th key={h} className="px-4 py-3 font-medium">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {loading ? (
                    <tr>
                      <td colSpan={5} className="px-4 py-12 text-center font-mono text-xs text-slate-500">
                        Sincronizando flota...
                      </td>
                    </tr>
                  ) : vehicles.length ? (
                    vehicles.map((v) => (
                      <tr key={v.id} className="transition hover:bg-ink/60">
                        <td className="px-4 py-4 font-semibold">
                          {v.brand} {v.model}
                        </td>
                        <td className="px-4 py-4 font-mono text-xs text-slate-400">
                          {v.internal_code || v.vin}
                        </td>
                        <td className="px-4 py-4 text-xs text-slate-300">{v.category || "—"}</td>
                        <td className="px-4 py-4 text-xs text-slate-400">
                          {v.taller_propietario || "Kartódromo Quito"}
                        </td>
                        <td className="px-4 py-4">
                          <select
                            value={v.status || "En box"}
                            disabled={updatingId === v.id}
                            onChange={(e) => handleStatusChange(v.id, e.target.value)}
                            className="rounded-lg border border-line bg-ink px-2 py-1.5 text-[11px] text-signal outline-none focus:border-signal disabled:opacity-50"
                          >
                            {FLEET_STATUSES.map((s) => (
                              <option key={s} value={s}>
                                {s}
                              </option>
                            ))}
                            {v.status &&
                              !(FLEET_STATUSES as readonly string[]).includes(v.status) && (
                                <option value={v.status}>{v.status}</option>
                              )}
                          </select>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={5} className="px-4 py-12 text-center text-sm text-slate-500">
                        No hay unidades. Registra la primera del piloto.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </section>
    </main>
  )
}
