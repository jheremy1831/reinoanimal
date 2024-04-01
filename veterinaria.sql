CREATE DATABASE veterinaria;

use veterinaria;
CREATE TABLE ROL(
  Id_Rol int AUTO_INCREMENT not null primary key,
  Nombre varchar(50),
  Sigla varchar(20),
  Jerarquia int
);

CREATE TABLE USUARIO(
  Id_Usuario Int AUTO_INCREMENT not null primary key,
  Usuario varchar(30),
  Contraseña varchar(100),
  Apellidos varchar(50),
  Nombres varchar(50),
  Email varchar(60),
  Sexo varchar(20),
  CI varchar(20),
  Celular varchar(20),
  Fecha_Nacimiento date,
  Rol_Id int,
  FOREIGN KEY (Rol_Id) REFERENCES ROL(Id_Rol)
);

CREATE TABLE CUENTA(
  Id_cuenta int AUTO_INCREMENT not null primary key,
  Estado_Usuario varchar(20),
  Foto_Perfil varchar(30),
  Usuario_Id int,
  FOREIGN KEY (Usuario_Id) REFERENCES USUARIO(Id_Usuario)
);

CREATE TABLE MASCOTA(
  Id_Mascota int AUTO_INCREMENT not null primary key,
  Nombre varchar(200),
  Edad varchar(20),
  Color_Pelo varchar(50),
  Raza varchar(50),
  Genero varchar(50),
  Usuario_Id int,
  FOREIGN KEY (Usuario_Id) REFERENCES USUARIO(Id_Usuario),
);
CREATE TABLE REGISTRO_CLINICO(
  Id_Registro int AUTO_INCREMENT not null primary key,
  Signos_Clinicos varchar(1000),
  Dia_1_Temperatura varchar(1000),
  Dia_2_Temperatura varchar(1000),
  Dia_3_Temperatura varchar(1000),
  Dia_4_Temperatura varchar(1000),
  Dia_5_Temperatura varchar(1000),
  Diagnostico varchar(500),
  Tratamiento varchar(500),  
  Duracion_del_Tratamiento varchar(500),
  Dia_1_Tratamiento_Farmaco varchar(1000),
  Dia_1_Tratamiento_Fecha date,
  Dia_2_Tratamiento_Farmaco varchar(1000),
  Dia_2_Tratamiento_Fecha date,
  Dia_3_Tratamiento_Farmaco varchar(1000),
  Dia_3_Tratamiento_Fecha date,
  Dia_4_Tratamiento_Farmaco varchar(1000),
  Dia_4_Tratamiento_Fecha date,
  Dia_5_Tratamiento_Farmaco varchar(1000),
  Dia_5_Tratamiento_Fecha date,
  Usuario_Id int,
  Mascota_Id int,
  FOREIGN KEY (Usuario_Id) REFERENCES USUARIO(Id_Usuario),
  FOREIGN KEY (Mascota_Id) REFERENCES MASCOTA(Id_Mascota)
);
----------------------------INSERTS ROL------------------------------------
use veterinaria;
INSERT INTO ROL
VALUES('','Administrador', 'ADM', 1);
INSERT INTO ROL
VALUES('','Veterinario', 'VET', 2);
INSERT INTO ROL
VALUES('','Asistente', 'ASI', 3);
INSERT INTO ROL
VALUES('','Cliente', 'CLI', 4);

