console.log('hello console!');


class Hello extends React.Component {

    render () {
        

        return (

                <p>Hello, World!</p>
        
        );
    }
}



ReactDOM.render(<Hello />, document.getElementById('root'));
