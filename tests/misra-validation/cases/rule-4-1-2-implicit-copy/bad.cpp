// Seeded violation: a class with a user-declared destructor that relies on its implicit copy constructor.
#include <cstdint>

namespace kv::rule_4_1_2_implicit_copy::bad {

class Buffer {
 public:
  explicit Buffer(std::uint32_t n) : n_(n) {}
  ~Buffer() { n_ = 0U; }  // user destructor, copy left implicit
  std::uint32_t size() const { return n_; }

 private:
  std::uint32_t n_;
};

std::uint32_t clone_size(const Buffer& b) {
  const Buffer c(b);  // uses the deprecated implicit copy constructor  // seeded
  return c.size();
}

}  // namespace kv::rule_4_1_2_implicit_copy::bad
