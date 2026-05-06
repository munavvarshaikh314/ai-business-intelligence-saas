import "@/styles/globals.css";
import { AuthProvider } from "@/context/AuthContext";
import { DatasetProvider } from "@/context/DatasetContext";
import { CreditsProvider } from "@/context/CreditsContext";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <DatasetProvider>
            <CreditsProvider>{children}</CreditsProvider>
          </DatasetProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
