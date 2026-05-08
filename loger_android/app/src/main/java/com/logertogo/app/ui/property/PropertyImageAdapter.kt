package com.logertogo.app.ui.property

import android.view.LayoutInflater
import android.view.ViewGroup
import android.widget.ImageView
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.logertogo.app.R
import com.logertogo.app.data.model.PropertyImage

class PropertyImageAdapter(
    private val images: List<PropertyImage>
) : RecyclerView.Adapter<PropertyImageAdapter.ViewHolder>() {

    class ViewHolder(val imageView: ImageView) : RecyclerView.ViewHolder(imageView)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val imageView = ImageView(parent.context).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            scaleType = ImageView.ScaleType.CENTER_CROP
        }
        return ViewHolder(imageView)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        Glide.with(holder.imageView.context)
            .load(images[position].image)
            .placeholder(R.color.grey_light)
            .into(holder.imageView)
    }

    override fun getItemCount() = images.size
}
