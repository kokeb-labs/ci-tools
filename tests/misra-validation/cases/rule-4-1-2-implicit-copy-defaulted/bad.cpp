// Seeded violation: the implicit copy constructor of a class with a user destructor.
#include <cstdint>

namespace kv::rule_4_1_2_implicit_copy_defaulted::bad {

class Buffer {
 public:
  explicit Buffer(std::uint32_t n) : n_(n) {}
  ~Buffer() { n_ = 0U; }
  std::uint32_t size() const { return n_; }

 private:
  std::uint32_t n_;
};
std::uint32_t clone_size(const Buffer& b) {
  const Buffer c(b);
  return c.size();
}

}  // namespace kv::rule_4_1_2_implicit_copy_defaulted::bad
