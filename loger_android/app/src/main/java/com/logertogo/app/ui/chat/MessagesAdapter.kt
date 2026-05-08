package com.logertogo.app.ui.chat

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.logertogo.app.data.model.Message
import com.logertogo.app.databinding.ItemMessageMeBinding
import com.logertogo.app.databinding.ItemMessageOtherBinding

class MessagesAdapter(
    private val currentUserId: String
) : ListAdapter<Message, RecyclerView.ViewHolder>(DiffCallback) {

    private val TYPE_ME = 1
    private val TYPE_OTHER = 2

    override fun getItemViewType(position: Int): Int {
        return if (getItem(position).sender.id == currentUserId) TYPE_ME else TYPE_OTHER
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return if (viewType == TYPE_ME) {
            MeViewHolder(ItemMessageMeBinding.inflate(LayoutInflater.from(parent.context), parent, false))
        } else {
            OtherViewHolder(ItemMessageOtherBinding.inflate(LayoutInflater.from(parent.context), parent, false))
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        val message = getItem(position)
        if (holder is MeViewHolder) holder.bind(message)
        else if (holder is OtherViewHolder) holder.bind(message)
    }

    class MeViewHolder(private val binding: ItemMessageMeBinding) : RecyclerView.ViewHolder(binding.root) {
        fun bind(message: Message) {
            binding.tvContent.text = message.content
            binding.tvTime.text = message.createdAt.substringAfter("T").substringBeforeLast(":")
            
            if (message.attachmentUrl != null) {
                binding.ivAttachment.visibility = View.VISIBLE
                Glide.with(binding.ivAttachment).load(message.attachmentUrl).into(binding.ivAttachment)
            } else {
                binding.ivAttachment.visibility = View.GONE
            }
        }
    }

    class OtherViewHolder(private val binding: ItemMessageOtherBinding) : RecyclerView.ViewHolder(binding.root) {
        fun bind(message: Message) {
            binding.tvContent.text = message.content
            binding.tvTime.text = message.createdAt.substringAfter("T").substringBeforeLast(":")
            
            if (message.attachmentUrl != null) {
                binding.ivAttachment.visibility = View.VISIBLE
                Glide.with(binding.ivAttachment).load(message.attachmentUrl).into(binding.ivAttachment)
            } else {
                binding.ivAttachment.visibility = View.GONE
            }
        }
    }

    companion object DiffCallback : DiffUtil.ItemCallback<Message>() {
        override fun areItemsTheSame(oldItem: Message, newItem: Message) = oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: Message, newItem: Message) = oldItem == newItem
    }
}
