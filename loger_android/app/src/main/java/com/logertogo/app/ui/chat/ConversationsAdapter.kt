package com.logertogo.app.ui.chat

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.logertogo.app.data.model.Conversation
import com.logertogo.app.databinding.ItemConversationBinding

class ConversationsAdapter(
    private val onConversationClick: (Conversation) -> Unit
) : ListAdapter<Conversation, ConversationsAdapter.ViewHolder>(DiffCallback) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemConversationBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val conversation = getItem(position)
        holder.bind(conversation)
    }

    inner class ViewHolder(private val binding: ItemConversationBinding) : RecyclerView.ViewHolder(binding.root) {
        fun bind(conversation: Conversation) {
            val otherParticipant = conversation.participants.firstOrNull { it.id != "CURRENT_USER_ID" } // Simplifié pour l'exemple
            binding.tvName.text = otherParticipant?.firstName ?: "Utilisateur"
            binding.tvLastMessage.text = conversation.lastMessage?.content ?: "Aucun message"
            
            // Formatage date simplifié
            binding.tvTime.text = conversation.updatedAt.substringBefore("T")

            Glide.with(binding.ivAvatar)
                .load(otherParticipant?.avatar)
                .placeholder(android.R.color.darker_gray)
                .circleCrop()
                .into(binding.ivAvatar)

            binding.root.setOnClickListener { onConversationClick(conversation) }
        }
    }

    companion object DiffCallback : DiffUtil.ItemCallback<Conversation>() {
        override fun areItemsTheSame(oldItem: Conversation, newItem: Conversation) = oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: Conversation, newItem: Conversation) = oldItem == newItem
    }
}
