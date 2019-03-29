import React from 'react';
import ReactDOM from 'react-dom';

//ReactDOM.render(<h1>hel</h1>, document.getElementById('query-app'));
import "./index.css";
import ReactTable from "react-table";
import "react-table/react-table.css";
//import matchSorter from 'match-sorter'
import DynamicForm from "react-dynamic-form";


class App extends React.Component {
  constructor(props) {    
    super(props);

    var formConfig = {
             fields: [
                 {
                     name: "sci_name",
                     title: "ID",
                     type: "text",
                 },
                 {
                     name: "family",
                     title: "科名",
                     type: "text",
                 },
                 {
                     name: "collector_id",
                     title: "採集者",
                     type: "select",
                   data: [],
                 },
                 {
                     name: "collector_num",
                     title: "採集號 (用 "-" 分隔)",
                     type: "text",
                 },
                 {
                     name: "creationDate",
                     title: "Created Date",
                     type: "date",
                 }
             ],
             primaryKey: "id"
};

    this.state = {
      isLoaded: false,
      formConfig: formConfig
    };

    
  }

  componentDidMount() {
    let url = `${window.location.origin}/api/query/hast`;
    //console.log('url', url);
    fetch(url) 
      .then(res => res.json())
      .then(
        (res_json) => {
          console.log('fetch', res_json);
          if (res_json['error'] != null) {
            const err = {message: res_json['error']}
            this.setState({
              error: err
            });                      
          }
          let fc = this.state.formConfig;
          res_json['menu']['collectors'].forEach(function(x) {
            fc.fields[2].data.push({name:x[0], title:x[1]});
          });

          this.setState({
            isLoaded: true,
            res: res_json,
            formConfig: fc
          });          
        },
        (error) => {
          this.setState({
            isLoaded: true,
            error
          });
        });
  }

 onSaveClicked() {
        console.log("SAve Clicked...");
        let data = this.boundForm.getData();
        if (data) {
            console.log("Data>>>", data);
        } else {
            console.log("Data Contains Errors...");
        }
 }
  
  render() {
    const { error, isLoaded, res } = this.state;
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
      return <div>Loading...</div>;
    } else {


      const cols = res.headers.map(function (h, hkey) {
        return (
          {
            Header: h.label,
            accessor: h.key
          })
      });
      //filterMethod: (filter, rows) =>
      //  matchSorter(rows, filter.value, { keys: ["lastName"] }),
      //filterAll: true

      const collector_options = res.menu.collectors.map(function(v, i){
        return <option value={v[0]} key={i}>{v[1]}</option>
      });
      return (
          <div>
          <div style={{'border': '1px solid black'}}>
          採集者 <select></select>
          採集號 <input type="text" /><input type="text" />
          <input type="submit" value="查詢" />
          </div>
          ----
          <select><option>--</option>{collector_options}</select>
          ----          
          <ReactTable
            manual // Forces table not to paginate or sort automatically, so we can handle it server-side
            data={res.rows}
            columns={cols} //[{Header: 'basic', columns: cols}]
            defaultPageSize={20}
            style={{
              height: "400px" // This will force the table body to overflow and scroll, since there is not enough room
            }}
            filterable        
            className="-striped -highlight"
          />
          <br />
          <div><center>HAST Query 2019</center></div>
          </div>
      );
    }
  }
}

ReactDOM.render(<App />, document.getElementById("query-hast"));
