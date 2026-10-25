"use client"

import { FormEvent, useCallback, useEffect, useState } from "react"
import { Activity, AlertTriangle, CarFront, CheckCircle2, RefreshCw, Server, Zap } from "lucide-react"
import { apiErrorCode, apiErrorMessage, createVehicle, listVehicles, Vehicle } from "@/lib/api"

const initialForm = { brand: "", model: "", vin: "", maintenance_type: "Diagnóstico Electrónico", taller_propietario: "Taller Central" }

export default function DashboardPage() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [form, setForm] = useState(initialForm)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")
  const [vinError, setVinError] = useState("")
  const [success, setSuccess] = useState("")
  const [lastSync, setLastSync] = useState<Date | null>(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    try { setVehicles(await listVehicles()); setLastSync(new Date()); setError("") }
    catch (err) { setError(apiErrorMessage(err)) }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { refresh(); const interval = window.setInterval(() => { if (!document.hidden) refresh() }, 15000); return () => window.clearInterval(interval) }, [refresh])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSaving(true); setError(""); setVinError(""); setSuccess("")
    const normalizedVin = form.vin.trim().toUpperCase()
    try {
      const created = await createVehicle({ ...form, vin: normalizedVin, status: "Diagnóstico" })
      if (created.id) setVehicles((current) => [{ ...created, ...form, vin: normalizedVin, id: created.id, status: "Diagnóstico" }, ...current])
      setSuccess("Unidad registrada y sincronizada con la flota."); setForm(initialForm); await refresh()
    } catch (err) {
      const message = apiErrorMessage(err)
      if (apiErrorCode(err) === "DUPLICATE_VIN") setVinError(message)
      else setError(message)
    } finally { setSaving(false) }
  }

  return <main className="min-h-screen bg-ink px-5 py-6 text-slate-100 md:px-10">
    <header className="mx-auto flex max-w-7xl items-center justify-between border-b border-line pb-6">
      <div className="flex items-center gap-3"><div className="grid size-10 place-items-center rounded-xl bg-signal text-ink"><Zap size={20} /></div><div><p className="font-mono text-[10px] uppercase tracking-[0.25em] text-signal">Multimakina / control room</p><h1 className="text-xl font-extrabold tracking-tight">Telemetría vehicular</h1></div></div>
      <div className="hidden items-center gap-3 text-xs text-slate-400 sm:flex"><span className="flex items-center gap-2"><span className="size-2 rounded-full bg-signal" /> API Render operativa</span><span className="rounded-full border border-line px-3 py-1 font-mono">v2.5</span></div>
    </header>
    <section className="mx-auto max-w-7xl py-8"><div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {[{ label: "Unidades registradas", value: vehicles.length, icon: CarFront }, { label: "Diagnósticos activos", value: vehicles.filter(v => v.status !== "Operativo").length, icon: Activity }, { label: "Voltaje promedio", value: "12.6 V", icon: Zap }, { label: "Estado del sistema", value: "Estable", icon: Server }].map(({ label, value, icon: Icon }) => <article key={label} className="rounded-2xl border border-line bg-panel p-5"><div className="mb-5 flex items-center justify-between"><p className="text-xs text-slate-400">{label}</p><Icon size={17} className="text-signal" /></div><p className="text-2xl font-bold">{value}</p></article>)}
    </div>
    <div className="grid gap-6 lg:grid-cols-[340px_1fr]">
      <section className="rounded-2xl border border-line bg-panel p-6"><div className="mb-6"><p className="font-mono text-[10px] uppercase tracking-[0.22em] text-signal">Nueva unidad</p><h2 className="mt-2 text-lg font-bold">Registrar vehículo</h2><p className="mt-1 text-xs leading-5 text-slate-400">Los datos se validan y persisten directamente en la API.</p></div>
        <form onSubmit={handleSubmit} className="space-y-4">{([["brand","Marca","Toyota"],["model","Modelo","Hilux 2.8"],["vin","VIN / chasis","17 caracteres"]] as const).map(([key, label, placeholder]) => <label key={key} className="block"><span className="mb-1.5 block text-xs font-semibold text-slate-300">{label}</span><input required minLength={key === "vin" ? 17 : 1} maxLength={key === "vin" ? 17 : 50} value={form[key]} onChange={e => { setForm({ ...form, [key]: e.target.value }); if (key === "vin") setVinError("") }} aria-invalid={key === "vin" && Boolean(vinError)} aria-describedby={key === "vin" && vinError ? "vin-error" : undefined} placeholder={placeholder} className={`w-full rounded-xl border bg-ink px-3.5 py-3 text-sm outline-none transition placeholder:text-slate-600 focus:border-signal ${key === "vin" && vinError ? "border-red-400" : "border-line"}`} />{key === "vin" && vinError && <span id="vin-error" className="mt-1.5 block text-xs text-red-300">{vinError}</span>}</label>)}
          <label className="block"><span className="mb-1.5 block text-xs font-semibold text-slate-300">Tipo de mantenimiento</span><select value={form.maintenance_type} onChange={e => setForm({ ...form, maintenance_type: e.target.value })} className="w-full rounded-xl border border-line bg-ink px-3.5 py-3 text-sm outline-none focus:border-signal"><option>Diagnóstico Electrónico</option><option>Preventivo</option><option>Correctivo</option></select></label>
          {error && <div role="alert" className="flex gap-2 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-xs leading-5 text-red-300"><AlertTriangle size={16} className="mt-0.5 shrink-0" />{error}</div>}{success && <div role="status" className="flex gap-2 rounded-xl border border-signal/30 bg-signal/10 p-3 text-xs leading-5 text-signal"><CheckCircle2 size={16} className="mt-0.5 shrink-0" />{success}</div>}
          <button disabled={saving} className="flex w-full items-center justify-center gap-2 rounded-xl bg-signal py-3 text-sm font-bold text-ink transition hover:bg-emerald-300 disabled:cursor-wait disabled:opacity-60">{saving && <RefreshCw size={15} className="animate-spin" />} {saving ? "Transmitiendo..." : "Registrar unidad"}</button>
        </form>
      </section>
      <section className="min-w-0 rounded-2xl border border-line bg-panel p-6"><div className="mb-6 flex items-start justify-between gap-4"><div><p className="font-mono text-[10px] uppercase tracking-[0.22em] text-signal">Live fleet</p><h2 className="mt-2 text-lg font-bold">Flota y diagnósticos activos</h2><p className="mt-1 text-xs text-slate-400">Actualización automática cada 15 segundos{lastSync && ` · última sincronización ${lastSync.toLocaleTimeString("es-CO")}`}</p></div><button onClick={refresh} disabled={loading} aria-label="Sincronizar flota" className="rounded-xl border border-line p-2.5 text-slate-300 hover:border-signal hover:text-signal"><RefreshCw size={16} className={loading ? "animate-spin" : ""} /></button></div>
        <div className="overflow-x-auto rounded-xl border border-line"><table className="w-full min-w-[620px] text-left text-sm"><thead className="bg-ink text-[10px] uppercase tracking-wider text-slate-500"><tr>{["Unidad","VIN","Diagnóstico","Taller","Estado"].map(h => <th key={h} className="px-4 py-3 font-medium">{h}</th>)}</tr></thead><tbody className="divide-y divide-line">{loading ? <tr><td colSpan={5} className="px-4 py-12 text-center font-mono text-xs text-slate-500">Sincronizando con Render...</td></tr> : vehicles.length ? vehicles.map(v => <tr key={v.id} className="transition hover:bg-ink/60"><td className="px-4 py-4 font-semibold">{v.brand} {v.model}</td><td className="px-4 py-4 font-mono text-xs text-slate-400">{v.vin}</td><td className="px-4 py-4 text-xs text-slate-300">{v.dtc_codes || "Sin códigos DTC"}</td><td className="px-4 py-4 text-xs text-slate-400">{v.taller_propietario || "Taller Central"}</td><td className="px-4 py-4"><span className="rounded-full bg-signal/10 px-2.5 py-1 text-[10px] font-semibold text-signal">{v.status || "Diagnóstico"}</span></td></tr>) : <tr><td colSpan={5} className="px-4 py-12 text-center text-sm text-slate-500">No hay unidades registradas todavía.</td></tr>}</tbody></table></div>
      </section>
    </div></section>
  </main>
}
