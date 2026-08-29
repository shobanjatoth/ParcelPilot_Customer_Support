// import React from 'react';

// const SUGGESTIONS = [
//   { icon: '📦', text: 'Track my parcel' },
//   { icon: '🚚', text: 'Where is my order?' },
//   { icon: '📅', text: 'When will my parcel arrive?' },
//   { icon: '💬', text: 'I need help with my delivery' },
// ];

// export default function WelcomeScreen({ onSuggestionClick }) {
//   return (
//     <div className="flex-1 flex items-center justify-center px-4 py-12">
//       <div className="text-center max-w-md animate-fade-in">
//         <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-700 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-primary-200">
//           <span className="text-4xl">📦</span>
//         </div>

//         <h2 className="text-2xl font-bold text-gray-900 mb-2">
//           ParcelPilot Customer Support
//         </h2>
//         <p className="text-gray-500 mb-8 leading-relaxed">
//           Your intelligent delivery assistant.
//           <br />
//           Ask me about your parcel, delivery,
//           <br />
//           tracking status, or account support.
//         </p>

//         <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
//           {SUGGESTIONS.map((s, i) => (
//             <button
//               key={i}
//               onClick={() => onSuggestionClick(s.text)}
//               className="flex items-center gap-3 px-4 py-3 bg-white border border-gray-200 rounded-xl text-left hover:border-primary-300 hover:shadow-md transition-all group"
//             >
//               <span className="text-xl">{s.icon}</span>
//               <span className="text-sm font-medium text-gray-700 group-hover:text-primary-600 transition-colors">
//                 {s.text}
//               </span>
//             </button>
//           ))}
//         </div>
//       </div>
//     </div>
//   );
// }




import React from 'react';
import { Package, Search, Calendar, Headphones, Sparkles, ChevronRight } from 'lucide-react';

const SUGGESTIONS = [
  { 
    title: 'Track my parcel', 
    desc: 'Get real-time updates on your parcel status', 
    icon: Package, 
    iconBg: 'bg-violet-50 text-violet-600 border border-violet-100' 
  },
  { 
    title: 'Where is my order', 
    desc: 'Find the current location of your order', 
    icon: Search, 
    iconBg: 'bg-blue-50 text-blue-600 border border-blue-100' 
  },
  { 
    title: 'When will my parcel arrive', 
    desc: 'Check estimated delivery date and time', 
    icon: Calendar, 
    iconBg: 'bg-emerald-50 text-emerald-600 border border-emerald-100' 
  },
  { 
    title: 'I need help with my delivery', 
    desc: 'Get support with delivery issues or special requests', 
    icon: Headphones, 
    iconBg: 'bg-orange-50 text-orange-500 border border-orange-100' 
  },
];

export default function WelcomeScreen({ onSuggestionClick }) {
  return (
    <div className="flex-1 flex items-center justify-center px-4 py-10 w-full">
      <div className="w-full max-w-4xl bg-white border border-slate-200/80 rounded-3xl shadow-xl shadow-slate-100 p-8 sm:p-12 text-center relative overflow-hidden animate-fade-in">
        
        {/* Top Floating Badge Icon */}
        <div className="w-12 h-12 rounded-2xl bg-violet-50 border border-violet-100 flex items-center justify-center mx-auto mb-5 text-violet-600 shadow-sm">
          <Sparkles className="w-6 h-6" />
        </div>

        {/* Heading & Subtitle */}
        <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 tracking-tight mb-3">
          Welcome to <span className="text-violet-600">ParcelPilot</span>
        </h2>
        <p className="text-sm sm:text-base text-slate-500 max-w-xl mx-auto mb-10 leading-relaxed">
          Your AI support assistant for all parcel and delivery-related queries. How can I help you today?
        </p>

        {/* 2x2 Interactive Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
          {SUGGESTIONS.map((s, i) => {
            const IconComponent = s.icon;
            return (
              <div
                key={i}
                onClick={() => onSuggestionClick(s.title)}
                className="group flex items-center justify-between p-5 bg-white hover:bg-slate-50/80 border border-slate-200/70 rounded-2xl cursor-pointer transition-all hover:shadow-md hover:border-violet-200"
              >
                <div className="flex items-center space-x-4">
                  <div className={`p-3 rounded-xl shrink-0 ${s.iconBg}`}>
                    <IconComponent className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900 text-sm group-hover:text-violet-600 transition-colors">
                      {s.title}
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5 leading-normal">
                      {s.desc}
                    </p>
                  </div>
                </div>
                <div className="w-7 h-7 rounded-full bg-slate-50 group-hover:bg-violet-50 flex items-center justify-center text-slate-400 group-hover:text-violet-600 transition-all shrink-0 ml-2">
                  <ChevronRight className="w-4 h-4" />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}