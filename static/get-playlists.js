"use strict";
//Example

$(document).ready(function() {
  console.log("got here");

  // const bookInfo = ([ ["book_id" , $("#bookid").val()], ["gr_id" , $("#grid").val()], ["description" , $("#bookdescription").html] ]);

  const bookInfo =  {"book_id" : $("#bookid").val(), "gr_id" : $("#grid").val(), "description" : $("#bookdescription").text()}

  function replacePlaylistResults(results) {
    // const playlist = results.map(x => x.name)

    for (let playlist of results) {
      const newElement = document.createElement('div');
      newElement.id = "playlist"; 
      newElement.innerHTML = playlist.name 
      document.body.appendChild(newElement);
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
