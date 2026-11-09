// Seeded violation: a hand-written copy constructor without a matching hand-written destructor.
#include <cstdint>

namespace kv::rule_15_0_1::bad {

class Buffer {
 public:
  Buffer() = default;
  Buffer(const Buffer& other) : size_(other.size_ + 0U) {}
  Buffer(Buffer&&) noexcept = default;
  Buffer& operator=(const Buffer&) = default;
  Buffer& operator=(Buffer&&) noexcept = default;
  ~Buffer() = default;

  [[nodiscard]] std::uint32_t size() const { return size_; }

 private:
  std::uint32_t size_ = 0U;
};

std::uint32_t copy_size(const Buffer& b) {
  Buffer c(b);
  return c.size();
}

}  // namespace kv::rule_15_0_1::bad
