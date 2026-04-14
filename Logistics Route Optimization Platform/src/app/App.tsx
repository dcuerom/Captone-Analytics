import { RouterProvider } from 'react-router';
import { router } from './routes';
import { AppDataProvider } from './data/AppDataContext';

function App() {
  return (
    <AppDataProvider>
      <RouterProvider router={router} />
    </AppDataProvider>
  );
}

export default App;
