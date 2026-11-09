// Seeded violation (template): a class template with a virtual base.
#include <cstdint>

namespace kv::rule_13_1_1::bad_template {

struct Base {
  std::int32_t tag = 0;
};

template <typename T>
struct Holder : virtual Base {  // seeded
  T item{};
};

std::int32_t tag_of(const Holder<std::int32_t>& h) { return h.tag; }

}  // namespace kv::rule_13_1_1::bad_template
