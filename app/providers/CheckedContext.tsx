import { createContext, ReactNode, useContext } from "react";

interface CheckedContextType {
  CheckedSquare: string;
  CheckingSquare: string;
}

const CheckedContext = createContext<CheckedContextType | undefined>(undefined);

interface CheckedProviderProps {
  CheckedSquare: string;
  CheckingSquare: string ;
  children: ReactNode;
}

export const CheckedProvider = ({children, CheckedSquare, CheckingSquare}: CheckedProviderProps) => {
    return (
    <CheckedContext.Provider value={{ CheckedSquare, CheckingSquare }}>
      {children}
    </CheckedContext.Provider>
    );
};

export const useChecked = (): CheckedContextType => {
  const context = useContext(CheckedContext);
  if (context === undefined) {
    throw new Error('useChecked must be used within a CheckedProvider');
  }
  return context;
}