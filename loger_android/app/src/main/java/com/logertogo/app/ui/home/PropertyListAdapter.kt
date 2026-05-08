package com.logertogo.app.ui.home

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.logertogo.app.R
import com.logertogo.app.data.model.Property
import com.logertogo.app.databinding.ItemPropertyBinding

class PropertyListAdapter(
    private val onClick: (Property) -> Unit,
    private val onFavoriteClick: (Property) -> Unit
) : ListAdapter<Property, PropertyListAdapter.ViewHolder>(DiffCallback) {

    class ViewHolder(val binding: ItemPropertyBinding) : RecyclerView.ViewHolder(binding.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemPropertyBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val property = getItem(position)
        holder.binding.apply {
            tvTitle.text = property.title
            tvPrice.text = root.context.getString(R.string.price_format, String.format("%,.0f", property.price))
            tvLocation.text = "${property.neighborhood}, ${property.city}"

            Glide.with(ivProperty.context)
                .load(property.mainImage)
                .centerCrop()
                .placeholder(R.color.grey_light)
                .into(ivProperty)

            root.setOnClickListener { onClick(property) }
            btnFavorite.setOnClickListener { onFavoriteClick(property) }
        }
    }

    companion object DiffCallback : DiffUtil.ItemCallback<Property>() {
        override fun areItemsTheSame(oldItem: Property, newItem: Property) = oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: Property, newItem: Property) = oldItem == newItem
    }
}
