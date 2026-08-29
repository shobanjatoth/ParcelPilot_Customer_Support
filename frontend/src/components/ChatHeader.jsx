// import React from 'react';

// const USER_OPTIONS = {
//   customer_northstar: 'Customer: Northstar Logistics',
//   customer_lumenworks: 'Customer: LumenWorks',
//   support_agent: 'Internal: Support Agent',
//   operations_admin: 'Internal: Operations Admin',
// };

// export default function ChatHeader({ userId, onClearChat, onChangeUser }) {
//   return (
//     <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200">
//       <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
//         <div className="flex items-center gap-3">
//           <div className="w-9 h-9 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-sm">
//             <span className="text-white text-lg">📦</span>
//           </div>
//           <div>
//             <h1 className="text-base font-semibold text-gray-900 leading-tight">ParcelPilot</h1>
//             <p className="text-xs text-gray-500">AI Support Agent</p>
//           </div>
//         </div>

//         <div className="flex items-center gap-3">
//           <select
//             value={userId}
//             onChange={(e) => onChangeUser(e.target.value)}
//             className="text-xs bg-gray-50 border border-gray-200 rounded-lg px-2 py-1.5 text-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent cursor-pointer"
//             aria-label="Select user"
//           >
//             {Object.entries(USER_OPTIONS).map(([key, label]) => (
//               <option key={key} value={key}>{label}</option>
//             ))}
//           </select>

//           <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 bg-green-50 rounded-full border border-green-200">
//             <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
//             <span className="text-xs font-medium text-green-700">AI Online</span>
//           </div>

//           <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 bg-gray-50 rounded-full border border-gray-200">
//             <svg className="w-3.5 h-3.5 text-gray-500" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
//               <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z" />
//             </svg>
//             <span className="text-xs font-medium text-gray-600">Secure</span>
//           </div>

//           <button
//             onClick={onClearChat}
//             className="px-3 py-1.5 text-xs font-medium text-gray-600 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
//             aria-label="Start new chat"
//           >
//             New Chat
//           </button>
//         </div>
//       </div>
//     </header>
//   );
// }




import React from 'react';
import { Building2, Sparkles, ChevronDown } from 'lucide-react';

const USER_OPTIONS = {
  customer_northstar: 'Northstar Logistics',
  customer_lumenworks: 'LumenWorks',
  support_agent: 'Support Agent',
  operations_admin: 'Operations Admin',
};

export default function ChatHeader({ userId, onClearChat, onChangeUser }) {
  return (
    <header className="flex items-center justify-between px-6 py-3.5 bg-white border-b border-slate-100 shadow-sm sticky top-0 z-20">
      {/* Brand Logo & Title */}
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-700 flex items-center justify-center shadow-md shadow-indigo-500/20 text-white">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
        </div>
        <div>
          <span className="font-bold text-slate-900 text-lg tracking-tight block leading-tight">ParcelPilot</span>
          <span className="text-[11px] text-slate-400 font-medium">AI Support Agent</span>
        </div>
      </div>

      {/* Middle/Right Controls */}
      <div className="flex items-center space-x-3">
        {/* Account Selector Pill */}
        <div className="flex items-center space-x-2 px-3 py-1.5 bg-slate-50 border border-slate-200/80 rounded-xl text-slate-700 text-xs font-medium cursor-pointer hover:bg-slate-100/80 transition-all">
          <Building2 className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          <select 
            value={userId} 
            onChange={(e) => onChangeUser(e.target.value)}
            className="bg-transparent border-none outline-none cursor-pointer text-slate-700 font-medium"
            aria-label="Select user"
          >
            {Object.entries(USER_OPTIONS).map(([key, label]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </div>

        {/* AI Online Status */}
        <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 bg-emerald-50/80 border border-emerald-200/50 rounded-full">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-xs font-semibold text-emerald-700">AI Online</span>
        </div>

        {/* New Chat Button */}
        <button 
          onClick={onClearChat}
          className="flex items-center space-x-1.5 px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white text-xs font-semibold rounded-xl shadow-md shadow-violet-500/20 transition-all active:scale-95"
          aria-label="Start new chat"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>New Chat</span>
        </button>

        {/* User Profile Avatar Dropdown Icon */}
        <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-600 hover:bg-slate-200 cursor-pointer transition-all">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <ChevronDown className="w-3 h-3 ml-0.5 text-slate-400 hidden sm:inline" />
        </div>
      </div>
    </header>
  );
}