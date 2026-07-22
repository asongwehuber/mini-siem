document.addEventListener(
    "DOMContentLoaded",
    function loadAlerts(page = 1){


        fetch("/alerts?page=" + page)


        .then(response => response.json())


        .then(data => {


            displayAlerts(data.alerts);


            updateAlertPagination(
                data.page,
                data.pages,
                data.total
            );


        })


        .catch(error => {


            console.error(
                "Error loading alerts:",
                error
            );


        });

    }

);

let allAlerts = [];


document.addEventListener(
    "DOMContentLoaded",
    function(){

        loadAlerts(1);

    }
);



function loadAlerts(page = 1){


    fetch("/alerts?page=" + page)


    .then(response => response.json())


    .then(data => {


        allAlerts = data.alerts;


        displayAlerts(
            data.alerts
        );


        updateAlertPagination(
            data.page,
            data.pages,
            data.total
        );


    })


    .catch(error => {


        console.error(
            "Error loading alerts:",
            error
        );


    });

}





function displayAlerts(alerts){


    let table =
        document.getElementById(
            "alerts-table"
        );


    table.innerHTML = "";


    let rows = "";



    alerts.forEach(alert => {



        rows += `

        <tr>


            <td>
                ${alert.id}
            </td>



            <td>
                ${alert.timestamp}
            </td>



            <td>

                <strong>
                ${alert.alert_name}
                </strong>

                <br>

                <small>
                ${alert.description}
                </small>

            </td>




            <td>

                <span class="severity-${alert.severity}">

                    ${alert.severity.toUpperCase()}

                </span>

            </td>




            <td>

                ${alert.source_ip || "-"}

            </td>




            <td>

                ${alert.event_count}

            </td>




            <td>

                ${alert.status}

            </td>




            <td>


                ${
                    alert.status === "OPEN"

                    ?

                    `

                    <button onclick="resolveAlert(${alert.id})">

                        ✅ Resolve

                    </button>

                    `

                    :

                    `✔ Closed`

                }



            </td>


        </tr>

        `;



    });



    table.innerHTML = rows;


}







function applyAlertFilters(){


    let search =
        document.getElementById(
            "search-input"
        )
        .value
        .toLowerCase();



    let severity =
        document.getElementById(
            "severity-filter"
        )
        .value;



    let status =
        document.getElementById(
            "status-filter"
        )
        .value;




    let filtered =
        allAlerts.filter(alert => {



            let ip =
                (alert.source_ip || "")
                .toLowerCase();



            return (


                (!search ||
                ip.includes(search))


                &&


                (!severity ||
                alert.severity === severity)


                &&


                (!status ||
                alert.status === status)


            );



        });




    displayAlerts(filtered);



}








function resolveAlert(id){


    fetch(
        "/resolve-alert/" + id,
        {
            method:"POST"
        }
    )



    .then(response => response.json())


    .then(data => {


        alert(
            data.message
        );


        loadAlerts();


    })



    .catch(error => {


        console.error(
            "Resolve error:",
            error
        );


    });



}

function updateAlertPagination(
    page,
    pages,
    total
){


    let info =
        document.getElementById(
            "alerts-info"
        );


    if(info){


        info.innerHTML =

        `
        Showing page ${page} of ${pages}
        (${total} total alerts)
        `;


    }



    let buttons =
        document.getElementById(
            "alerts-pagination-buttons"
        );


    if(!buttons)
        return;



    buttons.innerHTML = "";



    if(page > 1){


        buttons.innerHTML +=

        `

        <button onclick="loadAlerts(${page-1})">

            ◀ Previous

        </button>

        `;


    }



    if(page < pages){


        buttons.innerHTML +=


        `

        <button onclick="loadAlerts(${page+1})">

            Next ▶

        </button>

        `;


    }


}