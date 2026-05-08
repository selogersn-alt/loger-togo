package com.logertogo.app.ui.chat

import android.app.Activity.RESULT_OK
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.activity.result.contract.ActivityResultContracts
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.navArgs
import androidx.recyclerview.widget.LinearLayoutManager
import com.bumptech.glide.Glide
import com.google.android.material.snackbar.Snackbar
import com.logertogo.app.databinding.FragmentChatDetailBinding
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File

/**
 * ═══════════════════════════════════════════════
 * Fragment de messagerie individuelle
 * - Affichage des messages en temps réel (polling)
 * - Envoi AJAX sans rechargement
 * - Envoi de photos depuis la galerie
 * - Accepter / Refuser la conversation
 * ═══════════════════════════════════════════════
 */
class ChatDetailFragment : Fragment() {

    private var _binding: FragmentChatDetailBinding? = null
    private val binding get() = _binding!!

    private val viewModel: ChatViewModel by viewModels()
    private val args: ChatDetailFragmentArgs by navArgs()

    private lateinit var messagesAdapter: MessagesAdapter
    private var selectedImageUri: Uri? = null

    // Sélecteur d'image depuis la galerie
    private val imagePickerLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri ->
        uri?.let {
            selectedImageUri = it
            binding.ivAttachmentPreview.visibility = View.VISIBLE
            Glide.with(this).load(it).into(binding.ivAttachmentPreview)
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentChatDetailBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        setupInputArea()
        observeViewModel()

        viewModel.loadConversation(args.conversationId)
        viewModel.loadMessages(args.conversationId)
        viewModel.startPolling(args.conversationId)
    }

    private fun setupRecyclerView() {
        messagesAdapter = MessagesAdapter(getCurrentUserId())
        binding.recyclerMessages.apply {
            layoutManager = LinearLayoutManager(requireContext()).apply {
                stackFromEnd = true // Messages depuis le bas
            }
            adapter = messagesAdapter
        }
    }

    private fun setupInputArea() {
        // Bouton envoyer
        binding.btnSend.setOnClickListener {
            val content = binding.etMessage.text.toString().trim()
            if (content.isEmpty() && selectedImageUri == null) return@setOnClickListener

            val imagePart = selectedImageUri?.let { uri ->
                val file = getFileFromUri(uri)
                file?.let {
                    val requestFile = it.asRequestBody("image/*".toMediaTypeOrNull())
                    MultipartBody.Part.createFormData("attachment", it.name, requestFile)
                }
            }

            viewModel.sendMessage(
                conversationId = args.conversationId,
                content = content,
                attachment = imagePart
            )

            binding.etMessage.setText("")
            selectedImageUri = null
            binding.ivAttachmentPreview.visibility = View.GONE
        }

        // Bouton joindre photo
        binding.btnAttach.setOnClickListener {
            imagePickerLauncher.launch("image/*")
        }

        // Supprimer aperçu image
        binding.ivAttachmentPreview.setOnLongClickListener {
            selectedImageUri = null
            binding.ivAttachmentPreview.visibility = View.GONE
            true
        }
    }

    private fun observeViewModel() {
        viewModel.conversation.observe(viewLifecycleOwner) { conv ->
            if (conv != null) {
                // Afficher/masquer les boutons selon le statut
                when (conv.status) {
                    "PENDING" -> {
                        binding.layoutPendingActions.visibility = View.VISIBLE
                        binding.layoutInput.visibility = View.VISIBLE

                        binding.btnAccept.setOnClickListener {
                            viewModel.updateStatus(args.conversationId, "ACCEPTED")
                        }
                        binding.btnReject.setOnClickListener {
                            viewModel.updateStatus(args.conversationId, "REJECTED")
                        }
                    }
                    "REJECTED" -> {
                        binding.layoutPendingActions.visibility = View.GONE
                        binding.layoutInput.visibility = View.GONE
                        binding.tvClosedBanner.visibility = View.VISIBLE
                    }
                    else -> {
                        binding.layoutPendingActions.visibility = View.GONE
                        binding.layoutInput.visibility = View.VISIBLE
                    }
                }
            }
        }

        viewModel.messages.observe(viewLifecycleOwner) { messages ->
            messagesAdapter.submitList(messages)
            if (messages.isNotEmpty()) {
                binding.recyclerMessages.smoothScrollToPosition(messages.size - 1)
            }
        }

        viewModel.sendState.observe(viewLifecycleOwner) { state ->
            binding.btnSend.isEnabled = !state.isLoading
            state.error?.let {
                Snackbar.make(binding.root, it, Snackbar.LENGTH_SHORT).show()
            }
        }
    }

    private fun getCurrentUserId(): String {
        // En prod, on extrairait l'ID du JWT. Pour le moment, on utilise une constante ou on le récupère du TokenManager.
        return "1" // ID de test, à synchroniser avec votre profil
    }

    private fun getFileFromUri(uri: Uri): File? {
        return try {
            val inputStream = requireContext().contentResolver.openInputStream(uri)
            val file = File(requireContext().cacheDir, "chat_image_${System.currentTimeMillis()}.jpg")
            file.outputStream().use { output -> inputStream?.copyTo(output) }
            file
        } catch (e: Exception) {
            null
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        viewModel.stopPolling()
        _binding = null
    }
}
