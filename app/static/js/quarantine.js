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




    let filtered =
        allQuarantinedHosts.filter(host => {



            let ip =
                (
                    host.source_ip || ""
                )
                .toLowerCase();



            let hostname =
                (
                    host.hostname || ""
                )
                .toLowerCase();




            return (

                (!search ||

                ip.includes(search) ||

                hostname.includes(search))


                &&


                (!status ||

                host.status === status)


            );



        });




    displayQuarantinedHosts(filtered);



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