# ============================================================================ 
# TERRAFORM: OMNI-DROMENON-MACHINA GCP INFRASTRUCTURE
# Complete deployment: Cloud Run, Firestore, Memorystore, Cloud Storage
# ============================================================================ 

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "omni-dromenon-terraform-state"
    prefix = "production"
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

provider "google-beta" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# ============================================================================ 
# VARIABLES
# ============================================================================ 

variable "gcp_project_id" {
  type    = string
  default = "omni-dromenon"
}

variable "gcp_region" {
  type    = string
  default = "us-central1"
}

variable "environment" {
  type    = string
  default = "production"
}

variable "domain" {
  type    = string
  default = "omni-dromenon-engine.com"
}

# ============================================================================ 
# SERVICE ACCOUNT
# ============================================================================ 

resource "google_service_account" "omni_service_account" {
  account_id   = "omni-dromenon-sa"
  display_name = "Omni-Dromenon Service Account"
  description  = "Service account for omni-dromenon-engine deployment"
}



resource "google_project_iam_binding" "omni_firestore_editor" {
  project = var.gcp_project_id
  role    = "roles/datastore.user"
  members = [
    "serviceAccount:${google_service_account.omni_service_account.email}"
  ]
}

resource "google_project_iam_binding" "omni_storage_editor" {
  project = var.gcp_project_id
  role    = "roles/storage.objectUser"
  members = [
    "serviceAccount:${google_service_account.omni_service_account.email}"
  ]
}

# ============================================================================ 
# CLOUD RUN: CORE ENGINE
# ============================================================================ 

resource "google_cloud_run_service" "core_engine" {
  name     = "omni-dromenon-core"
  location = var.gcp_region

  template {
    spec {
      service_account_name = google_service_account.omni_service_account.email
      
      containers {
        image = "gcr.io/${var.gcp_project_id}/omni-dromenon-core:latest"
        
        ports {
          container_port = 3000
        }
        
        env {
          name  = "NODE_ENV"
          value = var.environment
        }
        env {
          name  = "LOG_LEVEL"
          value = "info"
        }
        env {
          name  = "REDIS_URL"
          value = "redis://${google_redis_instance.omni_cache.host}:${google_redis_instance.omni_cache.port}"
        }
        env {
          name  = "FIRESTORE_PROJECT_ID"
          value = var.gcp_project_id
        }
        env {
          name  = "GCP_REGION"
          value = var.gcp_region
        }
        env {
          name  = "CORS_ORIGIN"
          value = "https://${var.domain},https://www.${var.domain}"
        }
        
        resources {
          limits = {
            cpu    = "1"
            memory = "2Gi"
          }
        }
        
        liveness_probe {
          http_get {
            path = "/health"
            port = 3000
          }
          initial_delay_seconds = 30
          period_seconds        = 10
          timeout_seconds       = 5
          failure_threshold     = 3
        }
      }
      
      timeout_seconds = 600
    }
    
    metadata {
      annotations = {
        "run.googleapis.com/vpc-access-connector" = google_vpc_access_connector.connector.name
        "run.googleapis.com/vpc-access-egress"    = "private-ranges-only"
        "autoscaling.knative.dev/minScale" = "1"
        "autoscaling.knative.dev/maxScale" = "5"
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [
    google_redis_instance.omni_cache,
    google_firestore_database.omni_firestore
  ]
}

resource "google_cloud_run_service_iam_binding" "core_engine_public" {
  location = google_cloud_run_service.core_engine.location
  service  = google_cloud_run_service.core_engine.name
  role     = "roles/run.invoker"
  members = [
    "allUsers"
  ]
}

# ============================================================================ 
# CLOUD RUN: PERFORMANCE SDK (FRONTEND)
# ============================================================================ 

resource "google_cloud_run_service" "performance_sdk" {
  name     = "omni-dromenon-sdk"
  location = var.gcp_region
  
  template {
    spec {
      service_account_name = google_service_account.omni_service_account.email
      
      containers {
        image = "gcr.io/${var.gcp_project_id}/omni-dromenon-sdk:latest"
        
        ports {
          container_port = 3000
        }
        
        env {
          name  = "REACT_APP_API_URL"
          value = "https://${google_cloud_run_service.core_engine.status[0].url}"
        }
        
        resources {
          limits = {
            cpu    = "1"
            memory = "1Gi"
          }
        }
      }
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "1"
        "autoscaling.knative.dev/maxScale" = "5"
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_binding" "sdk_public" {
  location = google_cloud_run_service.performance_sdk.location
  service  = google_cloud_run_service.performance_sdk.name
  role     = "roles/run.invoker"
  members = [
    "allUsers"
  ]
}

# ============================================================================ 
# CLOUD RUN: LANDING PAGE
# ============================================================================ 

resource "google_cloud_run_service" "landing_page" {
  name     = "omni-dromenon-landing"
  location = var.gcp_region
  
  template {
    spec {
      containers {
        image = "gcr.io/${var.gcp_project_id}/omni-dromenon-landing:latest"
        ports {
          container_port = 80
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_binding" "landing_public" {
  location = google_cloud_run_service.landing_page.location
  service  = google_cloud_run_service.landing_page.name
  role     = "roles/run.invoker"
  members = [
    "allUsers"
  ]
}

# ============================================================================ 
# FIRESTORE DATABASE
# ============================================================================ 

resource "google_firestore_database" "omni_firestore" {
  project     = var.gcp_project_id
  name        = "omni-dromenon-db"
  location_id = var.gcp_region
  type        = "FIRESTORE_NATIVE"
  
  app_engine_integration_mode = "DISABLED"
}

# ============================================================================ 
# REDIS (MEMORYSTORE)
# ============================================================================ 

resource "google_redis_instance" "omni_cache" {
  name               = "omni-dromenon-cache"
  memory_size_gb     = 50
  tier               = "STANDARD_HA"
  region             = var.gcp_region
  redis_version      = "REDIS_6_X"
  display_name       = "Omni-Dromenon Redis Cache"
  authorized_network = google_compute_network.omni_network.id
  
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours = 2
      }
    }
  }
  
  auth_enabled = true
  
  labels = {
    app         = "omni-dromenon"
    environment = var.environment
  }
}

# ============================================================================ 
# CLOUD STORAGE
# ============================================================================ 

resource "google_storage_bucket" "omni_assets" {
  name          = "omni-dromenon-assets-${var.gcp_project_id}"
  location      = var.gcp_region
  force_destroy = false
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      num_newer_versions = 5
    }
    action {
      type = "Delete"
    }
  }
  
  labels = {
    app         = "omni-dromenon"
    environment = var.environment
  }
}

resource "google_storage_bucket" "omni_recordings" {
  name          = "omni-dromenon-recordings-${var.gcp_project_id}"
  location      = var.gcp_region
  force_destroy = false
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
  
  labels = {
    app         = "omni-dromenon"
    environment = var.environment
  }
}

# ============================================================================ 
# VPC NETWORK
# ============================================================================ 

resource "google_compute_network" "omni_network" {
  name                    = "omni-dromenon-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "omni_subnet" {
  name          = "omni-dromenon-subnet"
  ip_cidr_range = "10.0.0.0/16"
  region        = var.gcp_region
  network       = google_compute_network.omni_network.id
}

resource "google_vpc_access_connector" "connector" {
  name          = "omni-connector"
  region        = var.gcp_region
  network       = google_compute_network.omni_network.name
  ip_cidr_range = "10.8.0.0/28"
}

# ============================================================================ 
# CLOUD MONITORING & LOGGING
# ============================================================================ 

resource "google_monitoring_alert_policy" "core_engine_latency" {
  display_name = "Omni-Dromenon Core Engine - High Latency"
  combiner     = "OR"
  
  conditions {
    display_name = "Core Engine Response Time > 2s"
    condition_threshold {
      filter          = "metric.type=\"run.googleapis.com/request_latencies\" AND resource.labels.service_name=\"omni-dromenon-core\" AND resource.type=\"cloud_run_revision\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 2000
      
      aggregations {
        alignment_period  = "60s"
        per_series_aligner = "ALIGN_PERCENTILE_95"
      }
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.omni_email.name]
}

resource "google_monitoring_notification_channel" "omni_email" {
  display_name = "Omni-Dromenon Team Email"
  type         = "email"
  
  labels = {
    email_address = "team@omni-dromenon-engine.com"
  }
}

# ============================================================================ 
# OUTPUTS
# ============================================================================ 

output "landing_page_url" {
  value       = google_cloud_run_service.landing_page.status[0].url
  description = "Cloud Run service URL for landing page"
}

output "core_engine_url" {
  value       = google_cloud_run_service.core_engine.status[0].url
  description = "Cloud Run service URL for core engine"
}

output "performance_sdk_url" {
  value       = google_cloud_run_service.performance_sdk.status[0].url
  description = "Cloud Run service URL for performance SDK"
}

output "redis_host" {
  value       = google_redis_instance.omni_cache.host
  sensitive   = true
  description = "Redis instance host"
}

output "firestore_database" {
  value       = google_firestore_database.omni_firestore.name
  description = "Firestore database name"
}

output "assets_bucket" {
  value       = google_storage_bucket.omni_assets.name
  description = "Cloud Storage bucket for assets"
}

output "recordings_bucket" {
  value       = google_storage_bucket.omni_recordings.name
  description = "Cloud Storage bucket for recordings"
}