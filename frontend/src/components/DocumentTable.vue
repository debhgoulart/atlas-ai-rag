<script setup lang="ts">
import { FileText, CheckCircle2, Clock, AlertTriangle, Trash2, Cpu } from "lucide-vue-next";
import type { DocumentItem } from "@/types";

defineProps<{
  documents: DocumentItem[];
}>();

const emit = defineEmits<{
  (e: "delete", id: string): void;
}>();

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}
</script>

<template>
  <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-xs">
    <div v-if="documents.length === 0" class="p-8 text-center text-slate-400 text-sm">
      <FileText class="w-8 h-8 mx-auto mb-2 opacity-40" />
      Nenhum documento enviado ainda. Faça o upload acima para popular sua base de conhecimento.
    </div>

    <div v-else class="overflow-x-auto">
      <table class="w-full text-left text-sm text-slate-600">
        <thead class="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          <tr>
            <th class="px-5 py-3.5">Documento</th>
            <th class="px-4 py-3.5">Tamanho</th>
            <th class="px-4 py-3.5">Status</th>
            <th class="px-4 py-3.5">Chunks Vetorizados</th>
            <th class="px-4 py-3.5">Data de Envio</th>
            <th class="px-4 py-3.5 text-right">Ações</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="doc in documents" :key="doc.id" class="hover:bg-slate-50/50 transition-colors">
            <!-- Filename -->
            <td class="px-5 py-3.5 font-medium text-slate-900 flex items-center gap-2.5">
              <div class="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
                <FileText class="w-4 h-4" />
              </div>
              <span class="truncate max-w-xs" :title="doc.filename">{{ doc.filename }}</span>
            </td>

            <!-- Size -->
            <td class="px-4 py-3.5 text-slate-500 whitespace-nowrap">
              {{ formatBytes(doc.file_size_bytes) }}
            </td>

            <!-- Status Badge -->
            <td class="px-4 py-3.5 whitespace-nowrap">
              <span
                v-if="doc.status === 'completed'"
                class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200"
              >
                <CheckCircle2 class="w-3.5 h-3.5 text-emerald-500" />
                Concluído
              </span>
              <span
                v-else-if="doc.status === 'processing' || doc.status === 'pending'"
                class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200 animate-pulse"
              >
                <Clock class="w-3.5 h-3.5 text-blue-500" />
                Processando...
              </span>
              <span
                v-else
                class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-50 text-rose-700 border border-rose-200"
                :title="doc.error_message || 'Erro no processamento'"
              >
                <AlertTriangle class="w-3.5 h-3.5 text-rose-500" />
                Falha
              </span>
            </td>

            <!-- Chunks Count -->
            <td class="px-4 py-3.5 whitespace-nowrap">
              <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-mono font-medium bg-slate-100 text-slate-700">
                <Cpu class="w-3 h-3 text-slate-500" />
                {{ doc.chunk_count }} chunks
              </span>
            </td>

            <!-- Date -->
            <td class="px-4 py-3.5 text-slate-400 whitespace-nowrap text-xs">
              {{ new Date(doc.created_at).toLocaleDateString('pt-BR') }}
            </td>

            <!-- Actions -->
            <td class="px-4 py-3.5 text-right whitespace-nowrap">
              <button
                @click="emit('delete', doc.id)"
                class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                title="Excluir documento"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
