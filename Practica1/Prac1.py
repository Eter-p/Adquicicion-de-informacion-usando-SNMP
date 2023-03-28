from reportlab.platypus import SimpleDocTemplate, PageBreak, Paragraph, Spacer ,Table, Image, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from pysnmp.hlapi import *
import os

print("""\nSistema de Administracion de red
Practica 1 - Adquicicion de Informacion
Fabian Hernandez Hernandez 4CM14 2019630344""")

numDispositivos = 0

def menu():
	print("\n********** Menu **********\n")
	print("1. Agregar Dispositivo")
	print("2. Cambiar informacion de Dispositivo")
	print("3. Eliminar dispositivo")
	print("4. Generar Reporte")
	print("5. Salir")

def escribirArchivo(datos,nombreArchivo):
	archivo = open(nombreArchivo,"w")
	for x in range(len(datos)-1):
		archivo.write(datos[x]+"\n")
	archivo.write(datos[len(datos)-1])
	archivo.close()

def leerArchivo(nombreArchivo):
	archivo = open(nombreArchivo,"r")
	datos = list()
	data = archivo.readlines()
	for x in data:
		datos.append(x[:len(x)-1])
	datos[-1] = data[-1]
	archivo.close()
	return datos

def obtenerDispositivo():
	listaDispositivos = os.listdir("Dispositivos/")
	if len(listaDispositivos) == 0:
		print("!!! No exiten dispositivos !!!")
		exit()
	print("Indice\tDispositivo")
	i=0
	for dispositivo in listaDispositivos:
		i+=1
		print(str(i)+".\t"+dispositivo)
	nDispositivo = input("\nElija un dispositivo (indice): ")
	nomDispositivo = "Dispositivos/"+listaDispositivos[int(nDispositivo)-1]
	return nomDispositivo

def agregar():
	print("\n***** Agregar Dispositivo *****\n")
	global numDispositivos
	datos = list()
	datos.append(input("Comunidad: "))
	datos.append(input("Version de SNMP: "))
	datos.append(input("Puerto: "))
	datos.append(input("IP: "))
	numDispositivos+=1
	escribirArchivo(datos,"Dispositivos/Dispositivo"+str(numDispositivos))
	print("\n!!!! Dispisitivo Agregado !!!")

def cambiar():
	nomDispositivo = obtenerDispositivo()
	datos = leerArchivo(nomDispositivo)
	while(True):
		print("Indice\tDato")
		print("1.\tComunidad: "+datos[0])
		print("2.\tVersion de SNMP: "+datos[1])
		print("3.\tPuerto: "+datos[2])
		print("4.\tIP: "+datos[3])
		print("5.\tGuardar\n")
		ndato = input("Que valor desea cambiar (indice): ")
		if int(ndato)<1 or int(ndato)>5:
			print("\n!!! Opcion no valida!!!\n")
			continue
		if ndato==str(5):
			break
		datos[int(ndato)-1] = input("Nuevo valor: ")
		print("\n!!! Valor cambiado !!!\n")
	escribirArchivo(datos,nomDispositivo)
	print("\n!!! Archivo actualizado !!!")

def eliminar():
	print("\n***** Elmininar Dispositivo *****\n")
	os.remove(obtenerDispositivo())
	print("\n!!! Dispositivo eliminado !!!")

def reporte():
	dispositivo = obtenerDispositivo()
	datos = leerArchivo(dispositivo)

	doc = SimpleDocTemplate("Reporte"+dispositivo[13:]+".pdf", pagesize = A4)
	estilo1 = ParagraphStyle('estilo1',fontName='Times-Roman',fontSize=24,leading=20)
	estilo2 = ParagraphStyle('estilo2',fontName='Times-Roman',fontSize=12,leading=20)
	story=[]

	P1 = Paragraph("Administracion de Servivios en red", estilo1)
	P2 = Paragraph("Practica 1", estilo1)
	P3 = Paragraph("Fabian Hernandez Hernandez", estilo1)

	descripcion = consulta(datos[0],datos[3],"1.3.6.1.2.1.1.1.0").split()
	
	sistema = str()
	for x in descripcion:
		sistema = x
		if ("Linux" in x):
			break
		elif ("Windows" in x):
			break
	version = str()
	flag = False
	for x in descripcion:
		version = x
		if (flag):
				break
		if ("#" in x):
			break
		elif ("Version" in x):
			flag = True
		
	if ("Ubuntu" in version):
		I = Image('Logos/Ubuntu.jpg', width=100, height=100,hAlign='RIGHT')
	else:
		I = Image('Logos/Windows.jpg', width=100, height=100,hAlign='RIGHT')
	nomDispositivo = descripcion[1]+" "+descripcion[2]
	contacto = consulta(datos[0],datos[3],"1.3.6.1.2.1.1.4.0")
	ubicacion = consulta(datos[0],datos[3],"1.3.6.1.2.1.1.6.0")
	numInterfaces = consulta(datos[0],datos[3],"1.3.6.1.2.1.2.1.0")

	P4 = Paragraph("Sistema Operativo: "+sistema+" "+version, estilo2)
	P5 = Paragraph("Dispositivo: "+nomDispositivo, estilo2)
	P6 = Paragraph("Informacion de contacto: " +contacto, estilo2)
	P7 = Paragraph("Ubicacion: "+ubicacion, estilo2)
	P8 = Paragraph("Numero de Interfaces: " +numInterfaces, estilo2)

	datosTabla = [["Interfaz", "Estado"]]
	for x in range(int(numInterfaces)):
		if(x==5):
			break
		fila = list()
		fila.append(consulta(datos[0],datos[3],"1.3.6.1.2.1.2.2.1.2."+str(x+1)))
		estado = consulta(datos[0],datos[3],"1.3.6.1.2.1.2.2.1.7."+str(x+1))
		if estado=="1":
			fila.append("UP")
		elif estado == "2":
			fila.append("DOWN")
		elif estado == "3":
			fila.append("TESTING")
		else:
			fila.append("ERROR")
		datosTabla.append(fila)

	tabla = Table(data = datosTabla,
				style = [
						('GRID',(0,0),(-1,-1),0.5,colors.grey),
						('BOX',(0,0),(-1,-1),2,colors.black),
						('BACKGROUND', (0, 0), (-1, 0), colors.blue),
						]
				)
	story.append(P1)
	story.append(P2)
	story.append(P3)
	story.append(I)
	story.append(P4)
	story.append(P5)
	story.append(P6)
	story.append(P7)
	story.append(P8)
	story.append(tabla)
	story.append(Spacer(0,15))
	doc.build(story)

def consulta(comunidad,ip,objeto):
#	python3 /home/eter/Documentos/Redes3/Introduccion_SNMP-master/1-SNMPget-v1/v1-get.py
	iterator = getCmd(
		SnmpEngine(),
		CommunityData(comunidad, mpModel=0),
		UdpTransportTarget((ip, 161)),
		ContextData(),
		ObjectType(ObjectIdentity(objeto))
	)

	errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

	if errorIndication:
		print(errorIndication)

	elif errorStatus:
		print('%s at %s' % (errorStatus.prettyPrint(),
							errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))

	else:
		varBind = varBinds[0]
		return str(varBind[1])
#main
while(True):
	menu()
	opcion = input("\nElije una opcion: ")
	if opcion == str(1):
		agregar()
	elif opcion == str(2):
		cambiar()
	elif opcion == str(3):
		eliminar()
	elif opcion == str(4):
		reporte()
	elif opcion == str(5):
		break
	else:
		print("\n!!! Opcion no valida !!!")