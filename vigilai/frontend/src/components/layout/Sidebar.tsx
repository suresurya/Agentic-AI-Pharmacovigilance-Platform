import { NavLink } from 'react-router-dom'
import { Activity, FileText, Upload, BarChart2, Shield } from 'lucide-react'
import clsx from 'clsx'

const links = [
  { to: '/', label: 'Dashboard', icon: Activity, exact: true },
  { to: '/reports', label: 'Reports', icon: FileText },
  { to: '/batch', label: 'Batch Upload', icon: Upload },
  { to: '/analytics', label: 'Analytics', icon: BarChart2 },
]

export function Sidebar() {
  return (
    <aside className="w-60 bg-slate-900 text-white flex flex-col h-screen sticky top-0">
      <div className="px-5 py-5 border-b border-slate-700">
        <div className="flex items-center gap-2">
          <Shield className="text-blue-400" size={22} />
          <span className="font-bold text-lg tracking-tight">VigilAI</span>
          <span className="text-xs bg-blue-600 px-1.5 py-0.5 rounded ml-auto">2.0</span>
        </div>
        <p className="text-xs text-slate-400 mt-1">Pharmacovigilance Platform</p>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map(({ to, label, icon: Icon, exact }) => (
          <NavLink
            key={to}
            to={to}
            end={exact}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white',
              )
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="px-4 py-4 border-t border-slate-700">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-full bg-blue-500 flex items-center justify-center text-xs font-bold">O</div>
          <div>
            <p className="text-xs font-medium">Demo Officer</p>
            <p className="text-xs text-slate-400">officer@vigilai.demo</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
