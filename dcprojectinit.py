#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
"""
简要说明：
1. new work rep db user script
2. expdb & impdb from odi base to new work rep script
3. new dc stage and target db user script
4. generate .sql and .bat file
"""
class InitDCProject:
       def __init__(self,project_short,ls_gs,work_rep_base,dc_user_base):
              self.__str_date = datetime.datetime.now().strftime("%Y%m%d")
              self.__project_short = project_short
              self.__ls_gs = ls_gs
              self.__dc_user_base = dc_user_base

              self.__work_rep_init_file_name = '01_work_rep_init_script.sql'
              self.__work_rep_init_bat = '01_work_rep_init_script.bat'
              self.__expdp_impdp_file_name = '02_expdp_impdp_script.sql'
              self.__dc_schema_init_file_name = '03_dc_schema_init_script.sql'
              self.__dc_schema_init_bat = '03_dc_schema_init_script.bat'

              work_rep_init_bat_script = 'sqlplus dc/dc@{work_rep_base} @01_work_rep_init_script.sql'
              dc_schema_init_bat_script = 'sqlplus dc/dc@{dc_user_base} @03_dc_schema_init_script.sql'
              self.__work_rep_bat = work_rep_init_bat_script.format(work_rep_base= work_rep_base)
              self.__dc_schema_bat =dc_schema_init_bat_script.format(dc_user_base= dc_user_base)

# IS AND GS have different odi base
              if ls_gs.upper() == 'LS':
                  exp_db = 'rep_dla'
              else:
                  exp_db= 'rep_gs'
              self.__exp_db = exp_db


              # execute at work_rep_base
              self.__create_work_rep_sql = """
              create user  rep_{project_short}  identified by  rep_{project_short}  ; 
              grant connect,resource,create session,create view,create synonym,
               select any table,unlimited tablespace to rep_{project_short}; 
              grant dba to rep_{project_short};  """
              self.__exp_impdb_sql = """ 
              expdp {exp_db}/{exp_db}@o46g4 schemas={exp_db} dumpfile={exp_db}_{date}.dmp logfile={exp_db}_{date}.log directory=data_pump_dir;
              impdp rep_{project_short}/rep_{project_short}@o46g4 directory=data_pump_dir dumpfile={exp_db}_{date}.dmp logfile={exp_db}_{date}.log remap_schema={exp_db}:rep_{project_short} full=y ignore=y ;
              """

              #execute at dc_user_base
              self.__create_tablespace_sql =  """ 
              create tablespace tbs_{project_short} 
              datafile '/oradata/{dc_user_base}/tbs_{project_short}_01.dbf' size 50m autoextend on  ,         
               '/oradata/{dc_user_base}/tbs_{project_short}_02.dbf' size 50m autoextend on    ;   """
              self.__create_stage_user_sql = """
              create user  {project_short}_{ls_gs}_src  identified by  {project_short}_{ls_gs}_src default tablespace tbs_{project_short}  ;  
              grant connect,resource,create session,create view,create synonym,
               select any table,unlimited tablespace to {project_short}_{ls_gs}_src ; 
              grant dba to {project_short}_{ls_gs}_src;  """
              self.__create_target_user_sql = """
              create user  {project_short}_{ls_gs}_tar  identified by  {project_short}_{ls_gs}_tar default tablespace tbs_{project_short}  ;  
              grant connect,resource,create session,create view,create synonym,
               select any table,unlimited tablespace to {project_short}_{ls_gs}_tar ; 
              grant dba to {project_short}_{ls_gs}_tar;  """


       # 1 生成work rep 创建的脚本
       def work_rep_init_script(self):
              script= self.__create_work_rep_sql.format(project_short=self.__project_short)
              return script
              pass
       # 2 生成expdb impdb 的脚本
       def expdp_impdp_script(self):
              script = self.__exp_impdb_sql.format(exp_db = self.__exp_db,project_short=self.__project_short, date=self.__str_date)
              return script
              pass
       # 3 生成dc schema 创建的脚本
       def dc_schema_init_script(self):
              script = self.__create_tablespace_sql.format(project_short = self.__project_short,dc_user_base = self.__dc_user_base) + '\n' + self.__create_stage_user_sql.format(project_short = self.__project_short,ls_gs = self.__ls_gs) + '\n' \
                     + self.__create_target_user_sql.format(project_short = self.__project_short,ls_gs = self.__ls_gs) + '\n'
              return script
              pass
       # 1.1 保存到 00_work_rep_init_script.sql
       def save_work_rep_init_script(self):
              f = open(self.__work_rep_init_file_name,'w+')
              f.write(self.work_rep_init_script())
              f.close()
              f = open(self.__work_rep_init_bat,'w+')
              f.write(self.__work_rep_bat)
              f.close()
              pass
       # 1.2 保存到 00_expdp_impdp_script.sql
       def save_expdp_impdp_script(self):
              f = open(self.__expdp_impdp_file_name,'w+')
              f.write(self.expdp_impdp_script())
              f.close()
              pass
       # 1.3 保存到 00_dc_schema_init_script.sql
       def save_dc_schema_init_script(self):
              f = open(self.__dc_schema_init_file_name,'w+')
              f.write(self.dc_schema_init_script())
              f.close()
              f = open(self.__dc_schema_init_bat,'w+')
              f.write(self.__dc_schema_bat)
              f.close()
              pass


if __name__=='__main__':
       project_short = ''
       work_rep_base = ''
       dc_user_base = ''
       ls_gs = ''
       # Test
       init_odi = InitDCProject('POC','LS','o46g4','o46g4')
       work_rep_init_script = init_odi.save_work_rep_init_script()
       expdp_impdp_script = init_odi.save_expdp_impdp_script()
       dc_schema_init_script = init_odi.save_dc_schema_init_script()
