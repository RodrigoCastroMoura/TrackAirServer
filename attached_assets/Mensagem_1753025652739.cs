using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;
using RastreioFacil.Domain.DTO;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RastreioFacil.Domain.Entities
{
    public class Mensagem
    {
        [BsonRepresentation(BsonType.ObjectId)]
        public string _id { get; private set; }

        public string cpf { get; private set; }

        public string IMEI { get; private set; }

        public int  id_tipo_Mensagem { get; private set; }

        public string ds_mensagem { get; private set; }

        public string ds_mensagemHtml { get; private set; }

        public DateTime? dt_mensagem { get; private set; }

        public bool? fl_lida { get; private set; }

        public virtual TipoMensagem tipoMensagem { get; set; }


        private Mensagem(MensagemDto mensagem)
        {
            if (mensagem != null) { 

                this._id = mensagem._id;
                this.cpf = mensagem.cpf;
                this.IMEI = mensagem.IMEI;
                this.id_tipo_Mensagem = mensagem.id_tipo_Mensagem;
                this.ds_mensagem = mensagem.ds_mensagem;
                this.dt_mensagem = mensagem.dt_mensagem;
                this.fl_lida = mensagem.fl_lida;
                this.ds_mensagemHtml = mensagem.ds_mensagemHtml;
            }
        }

       public static Mensagem RetornoMensagem(MensagemDto mensagemDto)
       {
           return new Mensagem(mensagemDto);
       }           
       
    }
}

