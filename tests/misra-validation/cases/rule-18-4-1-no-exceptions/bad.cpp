// Seeded violation of the claimed query (from the main case), so the case also proves detection.
#include <cstdint>

namespace kv::rule_18_4_1_no_exceptions::bad {

class Block {
 public:
  Block() = default;
  Block(const Block&) = default;
  Block(Block&& other) : size_(other.size_) {}  // seeded
  Block& operator=(const Block&) = default;
  Block& operator=(Block&&) noexcept = default;
  ~Block() = default;

 private:
  std::uint32_t size_ = 0U;
};

}  // namespace kv::rule_18_4_1_no_exceptions::bad
