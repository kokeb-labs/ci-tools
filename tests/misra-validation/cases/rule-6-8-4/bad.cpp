// Seeded violation: members returning a reference into the object are callable on a temporary.
#include <cstdint>

namespace kv::rule_6_8_4::bad {

class Buffer {
 public:
  std::int32_t const& first() const { return data_; }  // seeded
  Buffer& self() { return *this; }  // seeded

 private:
  std::int32_t data_{0};
};

}  // namespace kv::rule_6_8_4::bad
