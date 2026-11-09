// Seeded violation: an overrider gives its parameter a different default argument than the base.
#include <cstdint>

namespace kv::rule_13_3_2::bad {

class Filter {
 public:
  virtual ~Filter() = default;
  virtual std::int32_t apply(std::int32_t gain = 1) const { return gain; }
};

class Strong : public Filter {
 public:
  std::int32_t apply(std::int32_t gain = 4) const override { return gain; }  // seeded
};

std::int32_t run(const Filter& f) { return f.apply(); }

}  // namespace kv::rule_13_3_2::bad
