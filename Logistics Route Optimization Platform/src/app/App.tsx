import { RouterProvider } from 'react-router';
import { router } from './routes';
import { AppDataProvider } from './data/AppDataContext';
import { AuthProvider } from './data/AuthContext';

function App() {
  return (
    <AuthProvider>
      <AppDataProvider>
        <RouterProvider router={router} />
      </AppDataProvider>
    </AuthProvider>
  );
}

export default App;
