import Foundation
import SQLite3

class DBHelper
{
    init()
    {
        db = openDatabase()
        createTable()
    }

    let dbPath: String = "tab.sqlite"
    var db:OpaquePointer?
    
    func openDatabase() -> OpaquePointer?
    {
        let fileURL = try! FileManager.default.url(for: .documentDirectory, in: .userDomainMask, appropriateFor: nil, create: false)
            .appendingPathComponent(dbPath)
        var db: OpaquePointer? = nil
        if sqlite3_open(fileURL.path, &db) != SQLITE_OK
        {
            print("error opening database")
            return nil
        }
        else
        {
            print("Successfully opened connection to database at \(dbPath)")
            return db
        }
    }
    
    func createTable() {
        let createTableString = "CREATE TABLE IF NOT EXISTS tabs(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, date TEXT, tab TEXT);"
        var createTableStatement: OpaquePointer? = nil
        if sqlite3_prepare_v2(db, createTableString, -1, &createTableStatement, nil) == SQLITE_OK
        {
            if sqlite3_step(createTableStatement) == SQLITE_DONE
            {
                print("tabs table created.")
            } else {
                print("tabs table could not be created.")
            }
        } else {
            print("CREATE TABLE statement could not be prepared.")
        }
        sqlite3_finalize(createTableStatement)
    }
    
    
    func insert(title:String, date:String, tab:String)
    {
        let insertStatementString = "INSERT INTO tabs (title, date, tab) VALUES (?, ?, ?);"
        var insertStatement: OpaquePointer? = nil
        if sqlite3_prepare_v2(db, insertStatementString, -1, &insertStatement, nil) == SQLITE_OK {
            sqlite3_bind_text(insertStatement, 1, (title as NSString).utf8String, -1, nil)
            sqlite3_bind_text(insertStatement, 2, (date as NSString).utf8String, -1, nil)
            sqlite3_bind_text(insertStatement, 3, (tab as NSString).utf8String, -1, nil)
            
            if sqlite3_step(insertStatement) == SQLITE_DONE {
                print("Successfully inserted row.")
            } else {
                print("Could not insert row.")
            }
        } else {
            print("INSERT statement could not be prepared.")
        }
        sqlite3_finalize(insertStatement)
    }
    
    func read(title: String) -> Tab {
        let queryStatementString = "SELECT * FROM tabs WHERE title = ?;"
        var queryStatement: OpaquePointer? = nil
        var psns : Tab!
        if sqlite3_prepare_v2(db, queryStatementString, -1, &queryStatement, nil) == SQLITE_OK {
            sqlite3_bind_text(queryStatement, 1, (title as NSString).utf8String, -1, nil)
            while sqlite3_step(queryStatement) == SQLITE_ROW {
                let id = sqlite3_column_int(queryStatement, 0)
                let title = String(describing: String(cString: sqlite3_column_text(queryStatement, 1)))
                let date = String(describing: String(cString: sqlite3_column_text(queryStatement, 2)))
                let tab = String(describing: String(cString: sqlite3_column_text(queryStatement, 3)))
                
                psns = Tab(id: Int(id), title: title, date: date, tab: tab)
                //print("\(id) | \(title) | \(date) | \(tab)")
            }
        } else {
            print("SELECT statement could not be prepared")
        }
        sqlite3_finalize(queryStatement)
        return psns
    }
    
    func readAll() -> [Tab] {
        let queryStatementString = "SELECT * FROM tabs;"
        var queryStatement: OpaquePointer? = nil
        var psns : [Tab] = []
        if sqlite3_prepare_v2(db, queryStatementString, -1, &queryStatement, nil) == SQLITE_OK {
            //print("Query Result:")
            while sqlite3_step(queryStatement) == SQLITE_ROW {
                let id = sqlite3_column_int(queryStatement, 0)
                let title = String(describing: String(cString: sqlite3_column_text(queryStatement, 1)))
                let date = String(describing: String(cString: sqlite3_column_text(queryStatement, 2)))
                let tab = String(describing: String(cString: sqlite3_column_text(queryStatement, 3)))
                
                psns.append(Tab(id: Int(id), title: title, date: date, tab: tab))
                //print("\(id) | \(title) | \(date) | \(tab)")
            }
        } else {
            print("SELECT statement could not be prepared")
        }
        sqlite3_finalize(queryStatement)
        return psns
    }
    
    func delete() {
        let deleteStatementStirng = "DELETE FROM tabs;"
        var deleteStatement: OpaquePointer? = nil
        if sqlite3_prepare_v2(db, deleteStatementStirng, -1, &deleteStatement, nil) == SQLITE_OK {
            if sqlite3_step(deleteStatement) == SQLITE_DONE {
                print("Successfully deleted all rows.")
            } else {
                print("Could not delete row.")
            }
        } else {
            print("DELETE statement could not be prepared")
        }
        sqlite3_finalize(deleteStatement)
    }
    
    func deleteByID(title:String) {
        let deleteStatementStirng = "DELETE FROM tabs WHERE title = ?;"
        var deleteStatement: OpaquePointer? = nil
        if sqlite3_prepare_v2(db, deleteStatementStirng, -1, &deleteStatement, nil) == SQLITE_OK {
            sqlite3_bind_text(deleteStatement, 1, (title as NSString).utf8String, -1, nil)
            if sqlite3_step(deleteStatement) == SQLITE_DONE {
                print("Successfully deleted row.")
            } else {
                print("Could not delete row.")
            }
        } else {
            print("DELETE statement could not be prepared")
        }
        sqlite3_finalize(deleteStatement)
    }
    
}
