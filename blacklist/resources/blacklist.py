from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from models import Blacklist, db

class AddToBlacklist(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()

        # Verificar si el email ya existe en la lista negra
        existing_entry = Blacklist.query.filter_by(email=data['email']).first()
        if existing_entry:
            return {"message": "El email ya está en la lista negra"}, 400

        # Crear una nueva entrada en la lista negra
        new_entry = Blacklist(
            email=data['email'],
            app_uuid=data['app_uuid'],
            blocked_reason=data.get('blocked_reason'),
            ip_address=request.remote_addr
        )

        # Agregar y confirmar la entrada en la base de datos
        db.session.add(new_entry)
        db.session.commit()

        # Respuesta JSON
        return {"message": "Email added to blacklist"}, 201

class CheckBlacklist(Resource):
    @jwt_required()
    def get(self, email):
        # Buscar si el email está en la lista negra
        entry = Blacklist.query.filter_by(email=email).first()
        if entry:
            # Si está en la lista negra, devolver razón
            return {
                "is_blacklisted": True,
                "reason": entry.blocked_reason
            }, 200
        # Si no está en la lista negra
        return {
            "is_blacklisted": False
        }, 404
