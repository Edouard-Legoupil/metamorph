import React from "react";
import { useNavigate } from "react-router-dom";

export const CardSelectionDashboard: React.FC = () => {
  const navigate = useNavigate();
  const handleLogout = () => {
    localStorage.removeItem("API_KEY");
    navigate("/login");
  };
  return (
    <div>
      <h2>Card Selection Dashboard</h2>
      <p>WIP: Select or create a new knowledge card.</p>
      <button style={{ position: "absolute", top: 8, right: 24 }} onClick={handleLogout}>Logout</button>
    </div>
  );
};
export default CardSelectionDashboard;
