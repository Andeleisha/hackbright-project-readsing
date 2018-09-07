"use strict";
//Example

$(document).ready(function() {
  console.log("got here");

  // const bookInfo = ([ ["book_id" , $("#bookid").val()], ["gr_id" , $("#grid").val()], ["description" , $("#bookdescription").html] ]);

  const bookInfo =  {"book_id" : $("#bookid").val(), "gr_id" : $("#grid").val(), "description" : $("#bookdescription").text()}

  const resultsContainer = document.querySelector("#searchresults");

  function replacePlaylistResults(results) {
    // const playlist = results.map(x => x.name)
    resultsContainer.innerHTML = ""

    for (let playlist of results) {
      const newElement = document.createElement('div');
      newElement.id = "playlist"; 
      newElement.innerHTML = `
      <div id="playlist" class="card flex-row flex-wrap">
        <div class="col-auto">
          <div className="card-header border-0">
            <img id="playlistCover" src="${playlist["image"]}" height="150" width="150"/>
          </div>
        </div>

        <div class="col">
          <div className="card-block px-2">
            <h5>${playlist["name"]}</h5>
            <a href="${playlist["link"]}">
              <img src="/static/Spotify_Icon.png" height="50" width="50"/>
              Open in Spotify
            </a>
          </div>
        </div>
      </div>
      ` 
      resultsContainer.appendChild(newElement);
    }

    // $("#searchresults").text(
    //   for (let playlist of results) {
    //     const newElement = document.createElement('div');
    //     newElement.id = "playlist"; 
    //     newElement.innerHTML = playlist.name 
    //     document.body.appendChild(newElement);
    // }

      // );
    console.log(results)
  }

  $.post("/get-playlists", bookInfo, replacePlaylistResults);
  /*
  function getPlaylists(evt) {
    $.post("/get-playlists", bookInfo, replacePlaylistResults);
  }

  $("#searchresults").on("load", getPlaylists)
  */
});
