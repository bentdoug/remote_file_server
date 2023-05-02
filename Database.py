class Database():
    def __init__(self) -> None:
        self.csv = "csv.txt"
        self.db = {}

    def convert_txt_to_db(self):
        '''
        Goal: Convert the CSV text file to a database for Startup
        Parameters
        ----------
        None:
        ----------
        Returns
        self.db: Dictionary - The Dictionary that the Database will be in
        '''

        #CSV File will be <File Path>, <Hashcode>
        with open(self.csv, "r") as f:
            for x in f:
                line = x.split(',')
                self.db[line[0]] = line[1] #Save the File Path as the key and the Hashcode as the value
        return self.db
    
    def get_db(self):
        return self.db
    
    def write_to_txt(self):
        '''
        Goal: Once shut down is initalized, write the new-found information in the db to the CSV File
        Parameters
        ----------
        None:
        ----------
        Returns
        None
        '''
        with open(self.csv, "w") as f:
            for key in self.db:
                f.write("{}, {}\n".format(key, self.db[key]))

def save_file(title, data):
    '''
    Goal: Write data contents from string to a file
    Parameters
    ----------
    title: String - Title of the text file
    data: String - Data to put into a txt file
    ----------
    Returns
    None
    '''
    with open("bin/{}".format(title), "w") as f:
        f.write(data)
