import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Accueil from "./pages/Accueil.jsx";
import Produits from "./pages/Produits.jsx";
import Services from "./pages/Services.jsx";
import Smartsticks from "./pages/Smartsticks.jsx";
import Securite from "./pages/Securite.jsx";
import APropos from "./pages/APropos.jsx";
import Bienvenue from "./pages/Bienvenue.jsx";
import SeConnecter from "./pages/SeConnecter.jsx";
import NouveauContact from "./pages/NouveauContact.jsx";
import PlaqueStandard from "./pages/PlaqueStandard.jsx";
import PlaqueGold from "./pages/PlaqueGold.jsx";
import Sos from "./pages/Sos.jsx";
import Depannage from "./pages/Depannage.jsx";
import AdminLogin from "./pages/AdminLogin.jsx";
import SosAdmin from "./pages/SosAdmin.jsx";
import DepannageAdmin from "./pages/DepannageAdmin.jsx";
import SosOperator from "./pages/SosOperator.jsx";
import DepannageOperator from "./pages/DepannageOperator.jsx";
import VerifyEmail from "./pages/VerifyEmail.jsx";
import VerifyLogin from "./pages/VerifyLogin.jsx";
import ResetPassword from "./pages/ResetPassword.jsx";
import ChangePassword from "./pages/ChangePassword.jsx";
import SendOtpPassword from "./pages/SendOtpPassword.jsx";
import ProfilVehicule from "./pages/ProfilVehicule.jsx";
import ImprimerLicence from "./pages/ImprimerLicence.jsx";
import VehiclePublicView from "./pages/VehiclePublicView.jsx";
import ModePayment from "./pages/ModePayment.jsx";
import { RequireAdmin, RequireOperator, RequireUser } from "./admin/AdminLayout.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Accueil />} />
        <Route path="/produits" element={<Produits />} />
        {/* alias to match the live site URL */}
        <Route path="/accueil" element={<Produits />} />
        <Route 
          path="/services" 
          element={
            <RequireUser>
              <Services />
            </RequireUser>
          } 
        />
        <Route path="/smartsticks" element={<Smartsticks />} />
        <Route path="/securite" element={<Securite />} />
        <Route path="/securite-and-innovation" element={<Securite />} />
        <Route path="/a-propos" element={<APropos />} />
        <Route 
          path="/bienvenue" 
          element={
            <RequireUser>
              <Bienvenue />
            </RequireUser>
          } 
        />
        <Route 
          path="/dashboard" 
          element={
            <RequireUser>
              <Bienvenue />
            </RequireUser>
          } 
        />
        <Route path="/se-connecter" element={<SeConnecter />} />
        <Route path="/nouveau-contact" element={<NouveauContact />} />
        <Route path="/verify-email" element={<VerifyEmail />} />
        <Route path="/verify-login" element={<VerifyLogin />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route 
          path="/dashboard/change-password" 
          element={
            <RequireUser>
              <ChangePassword />
            </RequireUser>
          } 
        />
        <Route path="/dashboard/send-otp-password" element={<SendOtpPassword />} />
        <Route
          path="/dashboard/profil"
          element={
            <RequireUser>
              <ProfilVehicule />
            </RequireUser>
          }
        />
        <Route
          path="/dashboard/licence"
          element={
            <RequireUser>
              <ImprimerLicence />
            </RequireUser>
          }
        />
        <Route 
          path="/plaque-standard" 
          element={
            <RequireUser>
              <PlaqueStandard />
            </RequireUser>
          } 
        />
        <Route 
          path="/plaque-silver" 
          element={
            <RequireUser>
              <PlaqueStandard />
            </RequireUser>
          } 
        />
        <Route 
          path="/plaque-gold" 
          element={
            <RequireUser>
              <PlaqueGold />
            </RequireUser>
          } 
        />
        <Route 
          path="/sos" 
          element={
            <RequireUser>
              <Sos />
            </RequireUser>
          } 
        />
        <Route 
          path="/depannage" 
          element={
            <RequireUser>
              <Depannage />
            </RequireUser>
          } 
        />
        <Route 
          path="/urgence-depannage" 
          element={
            <RequireUser>
              <Depannage />
            </RequireUser>
          } 
        />
        {/* Public vehicle profile — accessible by anyone who scans the QR code */}
        <Route path="/vehicle/:qrCode" element={<VehiclePublicView />} />
        {/* Payment page */}
        <Route path="/mode-de-paiement" element={<ModePayment />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>

      {/* Admin routes */}
      <Route path="/admin" element={<AdminLogin />} />
      <Route
        path="/admin/sos"
        element={
          <RequireAdmin>
            <SosAdmin />
          </RequireAdmin>
        }
      />
      <Route
        path="/admin/depannage"
        element={
          <RequireAdmin>
            <DepannageAdmin />
          </RequireAdmin>
        }
      />

      {/* Operator routes */}
      <Route
        path="/operator/sos"
        element={
          <RequireOperator allowedRoles={["sos"]}>
            <SosOperator />
          </RequireOperator>
        }
      />
      <Route
        path="/operator/depannage"
        element={
          <RequireOperator allowedRoles={["depannage"]}>
            <DepannageOperator />
          </RequireOperator>
        }
      />
    </Routes>
  );
}
