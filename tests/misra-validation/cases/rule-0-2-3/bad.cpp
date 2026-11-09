// Seeded violation: private, file-local and block-scope types that nothing uses.
#include <cstdint>

namespace kv::rule_0_2_3::bad {

class Holder {
 public:
  std::uint32_t get() const { return value_; }

 private:
  struct Spare {  // nothing uses this private type
    std::uint32_t v;
  };
  std::uint32_t value_{0U};
};

std::uint32_t read(const Holder& h) { return h.get(); }

namespace {
struct Orphan {  // internal linkage, never used
  std::uint32_t v;
};
}  // namespace

std::uint32_t local(std::uint32_t v) {
  struct Unused {  // block-scope type, never used
    std::uint32_t w;
  };
  return v;
}

}  // namespace kv::rule_0_2_3::bad
