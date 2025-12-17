import { StrictMode } from 'react'
import ReactDOM from 'react-dom/client'
import AppFacebook from './AppFacebook.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppFacebook />
  </StrictMode>,
)