from odoo import http
from odoo.http import request
import base64
import logging

_logger = logging.getLogger(__name__)


class OnboardingController(http.Controller):
    """
    Public-facing onboarding portal controller.

    Handles two routes:
      - GET  /onboarding/<token>         → renders the onboarding form
      - POST /onboarding/<token>/submit  → processes and saves the submission

    Each onboarding record is identified by a unique token so the route
    is publicly accessible without requiring a login. Multi-company context
    is applied so records are reachable regardless of which company they
    belong to.
    """

    @http.route('/onboarding/<string:token>', type='http', auth='public', website=True)
    def onboarding_form(self, token, **kwargs):
        # Apply all company IDs so public route can reach any company's record
        all_company_ids = request.env['res.company'].sudo().search([]).ids

        record = request.env['x_client_onboarding'].sudo().with_context(
            allowed_company_ids=all_company_ids
        ).search([('x_onboarding_token', '=', token)], limit=1)

        if not record:
            return request.render('website.404')

        return request.render(
            'onboarding_form.portal_onboarding_form',
            {'record': record}
        )

    @http.route('/onboarding/<string:token>/submit', type='http', auth='public',
                methods=['POST'], website=True, csrf=True)
    def onboarding_submit(self, token, **post):
        # Apply all company IDs so public route can reach any company's record
        all_company_ids = request.env['res.company'].sudo().search([]).ids

        record = request.env['x_client_onboarding'].sudo().with_context(
            allowed_company_ids=all_company_ids
        ).search([('x_onboarding_token', '=', token)], limit=1)

        if not record:
            return request.render('website.404')

        vals = {}

        # ------------------------------------------------------------------
        # TEXT FIELDS
        # Each field name maps directly to a field on the onboarding model.
        # Only fields with submitted values are written to avoid overwriting
        # existing data with empty strings.
        # ------------------------------------------------------------------
        text_fields = [
            # General company information
            'x_studio_company_name',
            'x_studio_acn',
            'x_studio_business_address',
            'x_studio_website',

            # Primary contact
            'x_studio_primary_contact_name',
            'x_studio_position',
            'x_studio_mobile_number',
            'x_studio_email_address',
            'x_studio_accounts_email',

            # Operational details — Company A (Logistics)
            'x_studio_years_in_operation',
            'x_studio_standard_pallet_quantity',
            'x_studio_refrigerated_frozen_ambient',
            'x_studio_fleet_size',
            'x_studio_years_operating',
            'x_studio_public_liability_insurance_expiry',
            'x_studio_cargo_insurance_expiry',
            'x_studio_vehicle_registration_expiry',
            'x_studio_driver_licence_expiry',
            'x_refrigeration_calibration_expiry',
            'x_studio_nhvr_accreditation_expiry',
            'x_studio_workcover_status',
            'x_studio_monthy_freight_spend',
            'x_delivery_window',

            # Operational details — Company B (Security)
            'x_studio_security_master_licence_number',
            'x_studio_master_licence_expiry_date_1',
            'x_studio_iso_certifications',
            'x_studio_public_liability_insurer',
            'x_studio_public_liability_coverage_amount',
            'x_studio_public_liability_expiry',
            'x_studio_workers_compensation_provider',
            'x_studio_workers_compensation_expiry',
            'x_studio_number_of_guards_available',
            'x_studio_number_of_supervisors',
            'x_studio_number_of_patrol_vehicles',
            'x_studio_largest_deployment_managed',
            'x_studio_minimum_deployment_notice_required',
            'x_studio_guard_management_platform',
            'x_studio_major_clients',
            'x_studio_reference_contact_name',
            'x_studio_reference_contact_number',
            'x_studio_reference_email',

            # Operational details — Company C (Technology)
            'x_studio_kt_hosting_provider',
            'x_studio_kt_domain_registrar',
            'x_studio_kt_website_platform',
            'x_studio_kt_crm_platform',
            'x_studio_kt_erp_platform',
            'x_studio_kt_microsoft_tenant',
        ]

        for fname in text_fields:
            if post.get(fname):
                vals[fname] = post.get(fname)

        # ------------------------------------------------------------------
        # BOOLEAN FIELDS
        # HTML checkboxes only appear in POST data when checked.
        # bool(post.get(fname)) returns False for unchecked fields,
        # ensuring every boolean is always written — not just the checked ones.
        # ------------------------------------------------------------------
        boolean_fields = [
            # Company A — Logistics requirements
            'x_studio_warehouse_booking_required',
            'x_studio_pod_mandatory',
            'x_studio_temperature_monitoring',
            'x_studio_tailgate_required',
            'x_studio_forklift_required',
            'x_studio_time_slot_delivery_1',
            'x_studio_retail_delivery',
            'x_studio_dc_delivery',
            'x_studio_fragile_freight',
            'x_studio_manual_unload',
            'x_studio_pallet_exchange_required',
            'x_studio_pallet_freight',
            'x_studio_carton_freight',
            'x_studio_wharf_deliveries',

            # Company A — Fleet capabilities
            'x_studio_nvhr_compliant_1',
            'x_studio_refrigerated_capability_1',
            'x_studio_frozen_capability_1',
            'x_studio_ambient_capability_1',
            'x_studio_tailgate_trucks',
            'x_studio_b_double_capability',
            'x_studio_dg_certified',
            'x_studio_linehaul_capability',
            'x_studio_metro_capability',
            'x_studio_regional_capability',
            'x_studio_interstate_capability',
            'x_studio_van',
            'x_studio_ute',
            'x_studio_rigid',
            'x_studio_semi',
            'x_studio_b_double',
            'x_studio_prime_mover',
            'x_studio_curtainsider_1',
            'x_studio_vic_metro',
            'x_studio_vic_regional',
            'x_studio_nsw_metro',
            'x_studio_nsw_regional',
            'x_studio_sa',
            'x_studio_qld',
            'x_studio_act',
            'x_studio_retail_delivery_1',
            'x_studio_dc_delivery_1',
            'x_studio_white_glove',
            'x_studio_express',
            'x_studio_overnight',
            'x_studio_changeovers',

            # Company B — Security licensing & compliance
            'x_studio_crowd_control_licensed',
            'x_studio_firearms_licensed',
            'x_studio_white_card_capability',
            'x_studio_working_with_children_capability',
            'x_studio_national_police_check_process_in_place',
            'x_studio_asial_member_1',
            'x_studio_iso_certified',
            'x_studio_professional_indemnity_insurance',
            'x_studio_vehicle_insurance_held',
            'x_studio_cyber_insurance_held',
            'x_studio_personal_accident_insurance_held',
            'x_studio_claims_in_last_5_years',
            'x_studio_active_litigationfair_work_matters',

            # Company B — Security operational capabilities
            'x_studio_247_capability',
            'x_studio_control_room_capability',
            'x_studio_emergency_response_capability',
            'x_studio_regional_deployment_capability',
            'x_studio_gps_tracking_capability',
            'x_studio_digital_incident_reporting',
            'x_studio_nfc_patrol_system',
            'x_studio_bodycams_used',
            'x_studio_dashcams_used',
            'x_studio_visitor_management_system',
            'x_studio_client_portal_available',
            'x_studio_apiintegration_capability',

            # Company C — Technology services
            'x_studio_kt_website_development',
            'x_studio_kt_seo',
            'x_studio_kt_marketing',
            'x_studio_kt_ai_automation',
            'x_studio_kt_crm_setup',
            'x_studio_kt_odoo_setup',
            'x_studio_kt_it_support',
            'x_studio_kt_microsoft_365',
            'x_studio_kt_cloud_infrastructure',
            'x_studio_kt_process_consulting',
            'x_studio_kt_operations_consulting',
            'x_studio_kt_google_workspace',
            'x_studio_kt_xero',
            'x_studio_kt_myob',
            'x_studio_kt_shopify',
            'x_studio_kt_odoo',
            'x_studio_kt_monday',
            'x_studio_kt_seo_active',
            'x_studio_kt_google_analytics',
            'x_studio_kt_search_console',
            'x_studio_kt_google_business',
            'x_studio_kt_social_media_access',
            'x_studio_kt_zapier',
            'x_studio_kt_makecom',
            'x_studio_kt_api_integrations',
            'x_studio_kt_ai_agents',
            'x_studio_kt_workflow_automations',
        ]

        for fname in boolean_fields:
            vals[fname] = bool(post.get(fname))

        # ------------------------------------------------------------------
        # BINARY FIELDS (file uploads)
        # Files are read from the multipart form, base64-encoded, and stored
        # directly on the Odoo record as binary fields.
        # The filename is stored in a companion _filename field for display.
        # ------------------------------------------------------------------
        binary_fields = [
            # Company A — Logistics compliance documents
            'x_studio_insurance_certificates_1',
            'x_studio_carrier_agreement_1',
            'x_studio_compliance_document',
            'x_studio_refrigeration_certificates_1',
            'x_studio_drivers_license_1',
            'x_studio_vehicle_registrations_1',

            # Company B — Security compliance documents
            'x_studio_upload_master_licence',
            'x_studio_upload_workers_compensation_certificate',
            'x_studio_sample_incident_report',
            'x_studio_sample_patrol_report',
            'x_studio_sample_daily_activity_report',
            'x_studio_capability_statement',
            'x_studio_company_profile',
            'x_studio_client_references',
            'x_studio_testimonials_uploaded',
        ]

        for fname in binary_fields:
            file = request.httprequest.files.get(fname)
            if file and file.filename:
                file_data = base64.b64encode(file.read())
                vals[fname] = file_data
                vals[fname + '_filename'] = file.filename

        # Write all collected values to the record in a single operation
        if vals:
            record.sudo().write(vals)

        return request.render(
            'onboarding_form.portal_onboarding_thankyou',
            {'record': record}
        )
  
