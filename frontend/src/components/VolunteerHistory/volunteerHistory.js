import React, {useState, useEffect} from "react";
import styles from "./volunteerHistory.modules.css"
const data = [
    {
        date: "January 2024",
        description: "Feed 100 homeless people.",
        role: "Chogath"
    },
    {
        date: "June 2028",
        description: "Save 10 babies from a burning building",
        role: "Nami"
    },
    {
        date: "July 2023",
        description: "Saved 80 animals from drowning",
        role: "Nidalee"
    },
]

const VolunteerHistory = () =>{
    const [info, setInfo] = useState([]);
    useEffect(() =>{
        setInfo(data);
    }, []);
    return(
        <div class="volunteerHistoryContainer">
            <h2>Volunteer History</h2>
            <div class="historyContainer">
                {data.length === 0 ? (<h3>No volunteer history</h3>):(
                    info.map((entry, index) =>
                    <div key={index}>
                        <p><strong>Role:</strong> {entry.role}</p>
                        <p><strong>Date:</strong> {entry.date}</p>
                        <p><strong>Description:</strong> {entry.description}</p>
                    </div>
                    )
                )}
            </div>
        </div>
    )
};

export default VolunteerHistory;