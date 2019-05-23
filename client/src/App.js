import React, { Component } from 'react';
import './App.css';
import Button from "@material-ui/core/Button";
import AppBar from '@material-ui/core/AppBar';
import ToolBar from '@material-ui/core/AppBar';
import IconButton from '@material-ui/core/AppBar';
import MenuIcon from '@material-ui/core/AppBar';
import TextField from '@material-ui/core/TextField';
import { withStyles } from '@material-ui/core/styles';
import * as $ from 'jquery';
function shablon_f(txt,m) //основная функция, возвращающая резултат преобразования ФИО
{
	var mrez=[];//для промежуточного результата
	var symb="";//набор символов, получаемых от сервера
	var tm=[];//набор слов из нормализованного ФИО
	for(var i in m)
	{
		if(m[i]!=null)//проверка на наличие слова
		{
			symb+=i[0].toUpperCase();
			tm.push(m[i]);
		}
		else
		{
			symb+=i[0].toUpperCase();
			m[i]=" ";
			tm.push(" ");
		}
		
	}
	m=tm;
	var i=1;
	if(txt[0]!="\\")//обеспечение экранирования символа
	{
		mrez.push([symb.indexOf(txt[0].toUpperCase()),txt[0]])
	}
	else
	{
		mrez.push([-1,txt[1]]);
		i++;
	}
	for(i;i<txt.length;i++)//посимвольная обработка шаблона
	{
		if(txt[i]!="\\")
		{
			if(symb.indexOf(txt[i].toUpperCase())==mrez[mrez.length-1][0])
			{
				mrez[mrez.length-1][1]+=txt[i];
			}
			else
			{
				mrez.push([symb.indexOf(txt[i].toUpperCase()),txt[i]])
			}
		}
		else
		{
			mrez.push([-1,txt[i+1]])
			i+=1;			
		}
	}
	var rez="";//результат преобразования
	for(var i=0;i<mrez.length;i++)
	{
		if(mrez[i][0]==-1)//если не нужна замена
		{
			rez+=mrez[i][1];
		}
		else
		{
			if(mrez[i][1].length==1)//первая буква
			{
				if(mrez[i][1]==symb[mrez[i][0]])//проверка регистра
				{	
					rez+=m[mrez[i][0]][0];
				}
				else
				{
					rez+=m[mrez[i][0]][0].toLowerCase();
				}
			}
			else
			{
				if(mrez[i][1]==(symb[mrez[i][0]]+symb[mrez[i][0]].toLowerCase()))//с большой буквы
				{	
					rez+=m[mrez[i][0]];
				}
				if(mrez[i][1]==symb[mrez[i][0]].repeat(2))//всё большими буквами
				{
					rez+=m[mrez[i][0]].toUpperCase();
				}
				if(mrez[i][1]==symb[mrez[i][0]].repeat(2).toLowerCase())//всё маленькими буквами
				{
					rez+=m[mrez[i][0]].toLowerCase();
				}
			}
		}
	}
	return rez;
};

class KnopkaFilter extends Component
{
	mymethod(e)//убирает все строки, относящиеся к классу, соответствующему ошибке
	{
		$('.oshybka').remove();
	};
	render()
	{
		return(
			<Button variant="contained" onClick={this.mymethod}>Убрать строки с ошибками</Button>
		);
	};
}

class KnopkaSort extends Component
{
	mymethod(e)//производит сортировку по содержимому
	{
		var m= document.getElementsByClassName("zapis");
		m = Array.prototype.slice.call(m);
		m.sort(function(a, b){return a.innerHTML.localeCompare(b.innerHTML);});
		var t=document.getElementById("rez_div");
		for(var i in m)
		{
			t.appendChild(m[i]);
		}
	};
	render()
	{
		return(
			<Button variant="contained" onClick={this.mymethod}>Сортировка↓</Button>
		);
	};
}

class KnopkaSortObr extends Component
{
	mymethod(e)//производит сортировку по содержимому в обратном порядке
	{
		var m= document.getElementsByClassName("zapis");
		m = Array.prototype.slice.call(m);
		m.sort(function(a, b){return -a.innerHTML.localeCompare(b.innerHTML);});
		var t=document.getElementById("rez_div");
		for(var i in m)
		{
			t.appendChild(m[i]);
		}
	};
	render()
	{
		return(
			<Button variant="contained" onClick={this.mymethod}>↑</Button>
		);
	};
}

class KnopkaSpravka extends Component
{
	mymethod(e)//вставляет в контейнер для результатов справочную информацию
	{
		var t = document.getElementById("rez_div");
		t.innerHTML="Пример имени: Михаил Владимирович Петров<br>";
		t.innerHTML+="Пример шаблона: ИИ Оо Ф.<br>";
		t.innerHTML+="Пример результата: МИХАИЛ Владимирович П.<br>";
		t.innerHTML+="<b>Имя:</b><br>";
		t.innerHTML+="И -> М<br>";
		t.innerHTML+="и -> м<br>";
		t.innerHTML+="Ии -> Михаил<br>";
		t.innerHTML+="ИИ -> МИХАИЛ<br>";
		t.innerHTML+="ии -> михаил<br>";
		t.innerHTML+="<b>Аналогично: Ф - фамилия, О - отчество, П - пол, Н - номер (п/п)</b><br>";
		t.innerHTML+="Для предотвращения замены символа, экранируйте его:<br><b>\\Ф -> Ф</b><br>";
	}
	render()
	{
		return(
			<Button variant="contained" onClick={this.mymethod}>Справка</Button>
		);
	}
}

class Knopka extends Component
{
	constructor(props)
	{
		super(props);
		this.mymethod=this.mymethod.bind(this);
	}
	
	mymethod(e)
	{
		function tf(t)
		{
			if(document.getElementById("shablon_vvod").value=="")
			{
				return;
			}
			if(document.getElementById("txt_vvod").value=="")
			{
				return;
			}
			return function(iof)
			{
				document.getElementById("rez_div").innerHTML="";
				var m=JSON.parse(iof);
				var sh=document.getElementById("shablon_vvod").value;
				for(var i in m)
				{
					iof=m[i];
					document.getElementById("rez_div").appendChild(document.createElement("div"));
					var prav=iof["Правильность"];
					delete iof["Правильность"];
					document.getElementById("rez_div").children[document.getElementById("rez_div").children.length-1].innerHTML=shablon_f(sh,iof);
					if(!prav)
					{
						document.getElementById("rez_div").children[document.getElementById("rez_div").children.length-1].className="ispravleno";
					}
					if(document.getElementById("rez_div").children[document.getElementById("rez_div").children.length-1].innerHTML.trim().length==0)
					{
						document.getElementById("rez_div").children[document.getElementById("rez_div").children.length-1].innerHTML="! ("+document.getElementById("txt_vvod").value.split("\n")[i]+")";
					}
					if((iof["Пол"]=="МЖ")||(iof["Пол"]=="Несоответствие"))
					{
						document.getElementById("rez_div").children[document.getElementById("rez_div").children.length-1].className="oshybka";
						document.getElementById("rez_div").children[document.getElementById("rez_div").children.length-1].innerHTML="! ("+document.getElementById("txt_vvod").value.split("\n")[i]+")";
					}
					
					document.getElementById("rez_div").children[document.getElementById("rez_div").children.length-1].classList.add("zapis");
					
					
				}
			}
			
		}
		const otvet=tf(this);
		document.getElementById("rez_div").innerHTML="";
		$.ajax
		(
			{
				type:"POST",
				url: "http://localhost:8765/",
				data: {"str":document.getElementById("txt_vvod").value.split("\n")},
				success:otvet
				
			}
		)

	}
	render()
	{
		return(
			<Button variant="contained" onClick={this.mymethod}>Обработать</Button>
		);
	};
}

class Vvod extends Component
{
	render()
	{
		const { classes  } = this.props;
		return(
			<TextField label="Шаблон" variant="outlined" placeholder="Ии Оо Ф." id="shablon_vvod" />
		);
	};
}

class TextVvod extends Component
{
	render()
	{
		return(
			<TextField label="Исходные имена" variant="outlined" multiline rowsMax="10" placeholder="Иванов Иван Иванович" id="txt_vvod" />
		);
	};
}

class Rezultat extends Component
{
	constructor(props)
	{
		super(props);
		
	}
	render()
	{
		return(
			<div id="rez_div" ></div>
		);
	};
}


class App extends Component
{
	b=[];
	render()
	{
		const { classes  } = this.props;
		
		return(
			<div className="App">
				<TextVvod />
				<br />
				<Vvod />
				<Knopka />  <KnopkaSpravka />
				<br />
				<KnopkaFilter />
				<KnopkaSort />
				<KnopkaSortObr />
				<br />
				<Rezultat />
			</div>
		);
	};
}


export default App;
