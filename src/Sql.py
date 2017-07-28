import pymysql as pm
import pickle


class sqlquery():

    def __init__(self):
        Mysql_host = 'ichs-interns-01-cluster.cluster-cgikkxxb8ppo.us-west-1.rds.amazonaws.com'
        Mysql_username = 'fanx'
        Mysql_password = 'GhQO8tUNUPd6IX8Z41HoO8b9C'
        Mysql_db = 'user_fanx'

        #Mysql_host = 'localhost'
        #Mysql_username = 'xfan'
        #Mysql_password = 'ZInGs7s#@nSpUppYAn0t0nkSt'
        #Mysql_db = 'metathesaurus'

        #self.con = pm.connect(Mysql_host, Mysql_username, Mysql_password, Mysql_db)
        self.con = pm.connect(read_default_file= "mys.conf")
        self.cur = self.con.cursor()

    # get query result
    def sql_query(self, keyword):

        try:
            #syntax = 'select b.str from MRXNW_ENG a, MRCONSO b where a.nwd = \'{}\' and a.cui = b.cui and b.tty = \'AUN\' limit 10;'.format(keyword)
            syntax = 'select b.str from MRXNW_ENG a, MRCONSO b where a.nwd = \'{}\' and a.cui = b.cui limit 10;'.format(keyword)
            self.cur.execute(syntax)
            results = self.cur.fetchall()
            #if results == ():
                #syntax = 'select b.str from MRXNW_ENG a, MRCONSO b where a.nwd = \'{}\' and a.cui = b.cui limit 10;'.format(keyword)
                #self.cur.execute(syntax)
                #results = self.cur.fetchall()
                #if results == ():
                #    results =
                #else:
                #    results = ()

        except:
            results = ['Error']
        return results

    def name_query(self, keyword):
        try:
            syntax = 'select b.str from MRXNW_ENG a, MRCONSO b where a.nwd = \'{}\' and a.cui = b.cui and b.tty = \'AUN\' limit 10;'.format(keyword)
            self.cur.execute(syntax)
            results = self.cur.fetchall()
        except:
            results = ['Error']
        return results

    def sql_close(self):
        self.con.close()


def main():
    sql = sqlquery()
    keyword = input('>')

    #with open('nameset.pkl','rb') as fin:
    #    nameset = pickle.load(fin)

    #for i in nameset:

    results = sql.sql_query(keyword)
    # print(type(results))
    #    if results == ():
    #        print(i)
    print(results == ())
    for i in results:
        print(i)

    sql.sql_close()


if __name__ == '__main__':
    main()
