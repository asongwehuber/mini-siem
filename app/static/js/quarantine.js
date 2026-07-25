let allQuarantinedHosts = [];



document.addEventListener(
    "DOMContentLoaded",
    function(){

        loadQuarantinedHosts(1);

    }
);





function loadQuarantinedHosts(page = 1){


    fetch("/quarantined-hosts?page=" + page)


    .then(response => response.json())


    .then(data => {


        allQuarantinedHosts = data.hosts;


        displayQuarantinedHosts(
            data.hosts
        );


        updateQuarantinePagination(
            data.page,
            data.pages,
            data.total
        );


        let count =
            document.getElementById(
                "quarantine-count"
            );


        if(count){

            count.innerHTML = data.total;

        }


    })


    .catch(error => {


        console.error(
            "Error loading quarantined hosts:",
            error
        );


    });


}







function displayQuarantinedHosts(hosts){


    let table =
        document.getElementById(
            "quarantine-table"
        );


    table.innerHTML = "";


    let rows = "";



    hosts.forEach(host => {



        rows += `

        <tr>


            <td>
                ${host.id}
            </td>



            <td>
                ${host.hostname || "-"}
            </td>



            <td>
                ${host.source_ip}
            </td>



            <td>
                ${host.reason}
            </td>



            <td>
                ${host.status}
            </td>



            <td>
                ${host.quarantined_at}
            </td>



            <td>


                ${
                    host.status === "quarantined"

                    ?

                    `

                    <button onclick="releaseHost(${host.id})">

                        ✅ Release

                    </button>

                    `

                    :

                    `
                    ✔ Released
                    `

                }


            </td>


        </tr>

        `;


    });



    table.innerHTML = rows;


}




function applyQuarantineFilters(){


    let search =
        document.getElementById(
            "search-input"
        )
        .value
        .toLowerCase();



    let status =
        document.getElementById(
            "status-filter"
        )
        .value;



    let period =
        document.getElementById(
            "time-filter"
        )
        .value;



    let start_time =
        document.getElementById(
            "start-time"
        )
        .value;



    let end_time =
        document.getElementById(
            "end-time"
        )
        .value;



    let params = new URLSearchParams();



    if(period){

        params.append(
            "period",
            period
        );

    }



    if(period === "custom"){


        params.append(
            "start_time",
            start_time
        );


        params.append(
            "end_time",
            end_time
        );

    }



    if(search){

        params.append(
            "search",
            search
        );

    }



    if(status){

        params.append(
            "status",
            status
        );

    }



    fetch(
        "/quarantined-hosts?" +
        params.toString()
    )


    .then(response => response.json())


    .then(data => {


        allQuarantinedHosts =
            data.hosts;



        displayQuarantinedHosts(
            data.hosts
        );


        updateQuarantinePagination(
            data.page,
            data.pages,
            data.total
        );


    })


    .catch(error => {


        console.error(
            "Filter error:",
            error
        );


    });


}




function releaseHost(id){



    fetch(
        "/release-host/" + id,
        {
            method:"POST"
        }
    )



    .then(response => response.json())


    .then(data => {


        alert(
            data.message
        );


        loadQuarantinedHosts(1);


    })



    .catch(error => {


        console.error(
            "Release error:",
            error
        );


    });



}









function updateQuarantinePagination(
    page,
    pages,
    total
){



    let info =
        document.getElementById(
            "quarantine-info"
        );



    if(info){


        info.innerHTML =

        `

        Showing page ${page} of ${pages}

        (${total} total quarantined hosts)

        `;


    }





    let buttons =
        document.getElementById(
            "quarantine-pagination-buttons"
        );



    if(!buttons)

        return;



    buttons.innerHTML = "";





    if(page > 1){


        buttons.innerHTML +=

        `

        <button onclick="loadQuarantinedHosts(${page-1})">

            ◀ Previous

        </button>

        `;


    }



    if(page < pages){


        buttons.innerHTML +=


        `

        <button onclick="loadQuarantinedHosts(${page+1})">

            Next ▶

        </button>

        `;


    }



}


function toggleCustomTime(){


    let selected =
        document.getElementById(
            "time-filter"
        ).value;



    let customBox =
        document.getElementById(
            "custom-time-range"
        );



    if(selected === "custom"){


        customBox.style.display =
            "flex";


    }
    else{


        customBox.style.display =
            "none";


        document.getElementById(
            "start-time"
        ).value = "";


        document.getElementById(
            "end-time"
        ).value = "";


    }


}