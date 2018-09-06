////////////////////////////////////////////////////////////////////////
//BookList
//callback function

function redirectSearch() {
    window.location.href="/search"
};

function postBookSelect(book_id) {
    // $.post("/bookselect", book_id, redirectSearch)
    
    fetch("/bookselect", {
            method: "POST",
            headers: {"Content-type" : "application/x-www-form-urlencoded; charset=UTF-8"},
            body : "book_id="+book_id
        })
        .then(() => redirectSearch());
};


const BookListItem = ({book, onBookSelect}) => {
    const imageURL = book.image;
    const bookName = book.name
    const book_id = book.gr_id
    const bookAuthor = book.author

//Use a callback function to make an AJAX/Fetch Post, then redirect separately (window.location.href=url)

    return (
        <div id="bookItem" className="card flex-row flex-wrap" onClick={() => postBookSelect(book_id)}> 
            
            <div className="col-auto">
                <div className="card-header border-0">
                    <img id="bookCover" src={imageURL} />
                </div>
            </div>
            
            <div className="col">
                <div className="card-block px-2">
                    <h5 id="bookTitle" className="card-title">{bookName}</h5>
                    <p id="bookAuthor" className="card-text">by {bookAuthor}</p>
                </div>
            </div>    
            
        </div>
    );


};

const BookList =  (props) => {
    const bookItems = props.books.map((book) => {

        return(
            <BookListItem
                onBookSelect={props.onBookSelect}
                key={book.gr_id}
                book={book} />
            );
    });

    return (
        <ul>
        {bookItems}
        </ul>
    );
};



/////////////////////////////////////////////////////////////////////////
//SearchBar
class SearchBar extends React.Component {
    constructor (props) {
        super(props);

        this.state = { term: ''};
    }

    render () {
        return (
            
            <div id="searchArea" className="center">
                <div className="row">
                    <div className="col center">
                        <div className="input-group input-group-lg" id="search-bar">
                            <input id="searchbox" className="form-control"
                                value={this.state.term}
                                onChange={event => this.onInputChange(event.target.value)} />
                            <div className="input-group-append">
                                <span className="input-group-text" id="basic-addon2">Search</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="row"> 
                    <div className="col">   
                        <p id="attribution" className="center">Search powered by Goodreads.</p>
                    </div>
                </div>
            </div>

        );
    }

    onInputChange(term) {
        this.setState({term})
        this.props.onSearchTermChange(term);
    }
}

////////////////////////////////////////////////////////////////////////
//Index
class App extends React.Component {
    constructor (props){
        super(props);

        this.state = {
            books: [],
            selectedBook: null
        };

        this._debouncedBookSearch = _.debounce( (term) => this._bookSearch(term), 500);

        this._recentBooks()
    }

    _bookSearch(term) {
        // const book_data = { "booksearch" : term }
        

        fetch("/interim-search", {
            method: "POST",
            headers: {"Content-type" : "application/x-www-form-urlencoded; charset=UTF-8"},
            body : "booksearch="+term
        })
            .then((response) => {
                return response.json();
            })
            .then((myJson) => {
                console.log(myJson)
                this.setState({
                    books : myJson
                })
            });
        

    }

    _recentBooks() {
        fetch("/recent-books")
            .then((response) => {
                return response.json();
            })
            .then((myJson) =>  {
                this.setState({ 
                    books: myJson 
                })
            });
    }

    render () {
        
        console.log(this.state)

        return (

                <div id="goodreadsSearch">
                    <SearchBar onSearchTermChange={this._debouncedBookSearch}/>
                    <BookList
                        onBookSelect={selectedBook => this.setState({selectedBook})}
                        books={this.state.books} />
                </div>
        
        );
    }
}



ReactDOM.render(<App />, document.getElementById('root'));
