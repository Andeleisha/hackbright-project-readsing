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
      <div class="playlist">
        <div>${playlist["name"]}</div>
        <div><img src="${playlist["image"]}"></div>
        <div><a href="${playlist["link"]}">Open in Spotify</a></div>
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
